"""Genera el modelo de datos desde los modelos de Django: conceptual, clases, lógico y físico.

Uso (desde la raíz del repositorio):
    python docs/diseno/datos.py

Escribe en docs/diseno/datos/ los .puml de los cuatro niveles y esquema.sql con el SQL de
PostgreSQL. No necesita un servidor de PostgreSQL: Django arma el SQL sin conectarse.
Si PLANTUML_JAR apunta a plantuml.jar, convierte además los diagramas a PNG en docs/diseno/img/.
"""
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'electrohogar.settings')

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.contrib.auth.models import Group, User  # noqa: E402
from django.db import models  # noqa: E402
from django.db.backends.postgresql.base import DatabaseWrapper  # noqa: E402

from inventario.models import Categoria, MovimientoStock, Producto  # noqa: E402
from ventas.models import DetalleVenta, Venta  # noqa: E402

AQUI = Path(__file__).parent
SALIDA = AQUI / 'datos'
IMG = AQUI / 'img'

# Modelos del sistema. De auth solo interesan el usuario y su rol (grupo).
MODELOS = [User, Group, Categoria, Producto, MovimientoStock, Venta, DetalleVenta]
NOMBRE = {User: 'Usuario', Group: 'Rol', Categoria: 'Categoria', Producto: 'Producto',
          MovimientoStock: 'MovimientoStock', Venta: 'Venta', DetalleVenta: 'DetalleVenta'}
# Del usuario de Django se muestran los campos que usa el sistema; el resto es de la librería.
CAMPOS_USUARIO = ['id', 'username', 'password', 'first_name', 'last_name', 'is_active', 'is_staff']

# Una conexión de PostgreSQL que nunca se abre: solo se usa para los tipos y el SQL.
cfg = dict(settings.DATABASES['default'])
cfg.update(ENGINE='django.db.backends.postgresql', NAME='electrohogar', USER='', PASSWORD='',
           HOST='', PORT='', OPTIONS={})
PG = DatabaseWrapper(cfg)
PG.pg_version = 160000

ESTILO = ['!include ../estilo.iuml', 'skinparam dpi 150', 'skinparam linetype ortho', 'skinparam classAttributeIconSize 0',
          'skinparam classBorderColor #333333', 'skinparam classBackgroundColor #FFFFFF',
          'skinparam classHeaderBackgroundColor #F7F7F7', 'hide circle', 'hide empty methods']


def campos(modelo):
    lista = [f for f in modelo._meta.concrete_fields]
    if modelo is User:
        lista = [f for f in lista if f.name in CAMPOS_USUARIO]
    return lista


def muchos_a_muchos():
    """La relación usuario-rol es la única de muchos a muchos (auth_user_groups)."""
    return User._meta.get_field('groups')


# --- Tipos de cada nivel ---------------------------------------------------

def tipo_logico(f):
    if isinstance(f, (models.AutoField, models.BigAutoField)):
        return 'entero'
    if isinstance(f, models.ForeignKey):
        return 'entero'
    if isinstance(f, models.DecimalField):
        return f'decimal({f.max_digits},{f.decimal_places})'
    if isinstance(f, models.DateTimeField):
        return 'fecha y hora'
    if isinstance(f, models.BooleanField):
        return 'lógico'
    if isinstance(f, (models.IntegerField,)):
        return 'entero ≥ 0' if isinstance(f, models.PositiveIntegerField) else 'entero'
    if isinstance(f, models.FileField):
        return f'texto({f.max_length}), ruta de la imagen'
    if isinstance(f, models.CharField):
        return f'texto({f.max_length})'
    return f.get_internal_type()


def tipo_clase(f):
    if isinstance(f, models.ForeignKey):
        return NOMBRE.get(f.related_model, f.related_model.__name__)
    return {
        'AutoField': 'int', 'BigAutoField': 'int', 'CharField': 'str', 'DecimalField': 'Decimal',
        'DateTimeField': 'datetime', 'BooleanField': 'bool', 'PositiveIntegerField': 'int',
        'IntegerField': 'int', 'FileField': 'Imagen',
    }.get(f.get_internal_type(), f.get_internal_type())


# --- Diagramas -------------------------------------------------------------

def conceptual():
    """Entidades y relaciones con su cardinalidad, en notación de Chen y sin atributos."""
    rel = [  # entidad A, cardinalidad A, relación, cardinalidad B, entidad B
        ('Categoria', '1', 'AGRUPA', 'N', 'Producto'),
        ('Producto', '1', 'CAMBIA_POR', 'N', 'MovimientoStock'),
        ('Usuario', '1', 'REGISTRA', 'N', 'MovimientoStock'),
        ('Usuario', '1', 'COBRA', 'N', 'Venta'),
        ('Usuario', '1', 'ANULA', 'N', 'Venta'),
        ('Venta', '1', 'CONTIENE', 'N', 'DetalleVenta'),
        ('Producto', '1', 'SE_VENDE_EN', 'N', 'DetalleVenta'),
        ('Usuario', 'N', 'TIENE', 'M', 'Rol'),
    ]
    out = ['@startchen', 'skinparam defaultFontName Arial', 'skinparam dpi 150', 'skinparam shadowing false',
           'skinparam backgroundColor #FFFFFF']
    for m in MODELOS:
        out += [f'entity {NOMBRE[m].upper()} {{', '}']
    for nombre in dict.fromkeys(r[2] for r in rel):
        out += [f'relationship {nombre} {{', '}']
    for a, ca, r, cb, b in rel:
        out.append(f'{a.upper()} -{ca}- {r}')
        out.append(f'{r} -{cb}- {b.upper()}')
    out.append('@endchen')
    return '\n'.join(out)


def clases():
    """Clases con atributos, propiedades y métodos, más los servicios que cambian el stock."""
    out = ['@startuml', *ESTILO, 'skinparam linetype polyline']
    metodos = {
        Producto: ['+bajo_minimo(): bool'],
        Venta: ['+calcular_total(): Decimal'],
        DetalleVenta: ['+subtotal(): Decimal'],
        User: ['+has_perm(permiso): bool'],
    }
    for m in MODELOS:
        out.append(f'class {NOMBRE[m]} {{')
        for f in campos(m):
            if f.primary_key:
                continue
            nombre = f.name
            if f.choices:
                opciones = ' | '.join(v for v, _ in f.choices)
                out.append(f'  {{field}} -{nombre}: {tipo_clase(f)} [{opciones}]')
            else:
                out.append(f'  {{field}} -{nombre}: {tipo_clase(f)}')
        for x in metodos.get(m, []):
            out.append(f'  {x}')
        out.append('}')
    out += [
        'class "inventario.servicios" as SI <<servicio>> {',
        '  +registrar_movimiento(producto, tipo, cantidad, usuario, motivo)',
        '  +ajustar_a_conteo(producto, contado, usuario, motivo)',
        '}',
        'class "ventas.servicios" as SV <<servicio>> {',
        '  +confirmar_venta(venta, cajero)',
        '  +anular_venta(venta, gerente, motivo)',
        '}',
        'Categoria "1" -- "0..*" Producto',
        'Producto "1" -- "0..*" MovimientoStock',
        'Usuario "1" -- "0..*" MovimientoStock : usuario',
        'Venta "1" *-- "1..*" DetalleVenta',
        'Producto "1" -- "0..*" DetalleVenta',
        'Usuario "1" -- "0..*" Venta : cajero',
        'Usuario "0..1" -- "0..*" Venta : anulada_por',
        'Usuario "0..*" -- "0..*" Rol : groups',
        'SV ..> SI : usa',
        'SI ..> MovimientoStock : crea',
        'SV ..> Venta : cambia estado',
    ]
    out.append('@enduml')
    return '\n'.join(out)


def tabla(m, fisico):
    nombre = m._meta.db_table if fisico else NOMBRE[m]
    filas = []
    for f in campos(m):
        col = f.column
        if fisico:
            tipo = f.db_type(PG)
            if isinstance(f, models.ForeignKey):
                tipo = f.target_field.rel_db_type(PG)
            extra = []
            if not f.null:
                extra.append('NOT NULL')
            if f.unique and not f.primary_key:
                extra.append('UNIQUE')
            chk = f.db_check(PG)
            if chk:
                extra.append('CHECK ≥ 0')
            detalle = f'{tipo} {" ".join(extra)}'.strip()
        else:
            detalle = tipo_logico(f) + ('' if not f.null else ', opcional')
        if f.primary_key:
            filas.insert(0, f'  {{field}} <b>PK</b> {col}: {detalle}')
        elif isinstance(f, models.ForeignKey):
            filas.append(f'  {{field}} <b>FK</b> {col}: {detalle}')
        else:
            filas.append(f'  {{field}} {col}: {detalle}')
    return nombre, filas


def relacional(fisico):
    out = ['@startuml', *ESTILO]
    for m in MODELOS:
        nombre, filas = tabla(m, fisico)
        out.append(f'entity "{nombre}" as {NOMBRE[m]} {{')
        out += filas
        out.append('}')
    # Tabla intermedia de usuario y rol.
    tm = muchos_a_muchos().remote_field.through
    inter = tm._meta.db_table if fisico else 'UsuarioRol'
    out.append(f'entity "{inter}" as UsuarioRol {{')
    if fisico:
        out += ['  {field} <b>PK</b> id: integer NOT NULL', '  {field} <b>FK</b> user_id: integer NOT NULL',
                '  {field} <b>FK</b> group_id: integer NOT NULL', '  {field} UNIQUE (user_id, group_id)']
    else:
        out += ['  {field} <b>PK</b> id: entero', '  {field} <b>FK</b> user_id: entero', '  {field} <b>FK</b> group_id: entero']
    out.append('}')
    out += [
        'Categoria ||--o{ Producto',
        'Producto ||--o{ MovimientoStock',
        'Usuario ||--o{ MovimientoStock',
        'Venta ||--|{ DetalleVenta',
        'Producto ||--o{ DetalleVenta',
        'Usuario ||--o{ Venta',
        'Usuario |o--o{ Venta',
        'Usuario ||--o{ UsuarioRol',
        'Rol ||--o{ UsuarioRol',
        '@enduml',
    ]
    return '\n'.join(out)


def esquema_sql():
    lineas = ['-- Esquema de ElectroHogar Ventas en PostgreSQL.',
              '-- Generado por docs/diseno/datos.py desde los modelos de Django; no se edita a mano.',
              '-- De las tablas auth_* de Django se listan el usuario, el rol (grupo) y la tabla que los une.', '']
    # Al crear el usuario, Django arma también sus tablas intermedias. Las de permisos se
    # omiten: son internas de Django y el sistema las usa a través de los roles.
    with PG.schema_editor(collect_sql=True, atomic=False) as ed:
        for m in [User, Group, Categoria, Producto, MovimientoStock, Venta, DetalleVenta]:
            ed.create_model(m)
    for s in dict.fromkeys(ed.collected_sql):
        if 'permission' not in s:
            lineas.append(s if s.endswith(';') else s + ';')
    return '\n'.join(lineas) + '\n'


def main():
    SALIDA.mkdir(exist_ok=True)
    archivos = {
        'modelo-conceptual.puml': conceptual(),
        'diagrama-de-clases.puml': clases(),
        'modelo-logico.puml': relacional(fisico=False),
        'modelo-fisico.puml': relacional(fisico=True),
    }
    for nombre, texto in archivos.items():
        (SALIDA / nombre).write_text(texto + '\n', encoding='utf-8')
    (SALIDA / 'esquema.sql').write_text(esquema_sql(), encoding='utf-8')
    print('Escritos:', ', '.join([*archivos, 'esquema.sql']))

    jar = os.environ.get('PLANTUML_JAR')
    if jar:
        IMG.mkdir(exist_ok=True)
        subprocess.run(['java', '-jar', jar, '-charset', 'UTF-8', '-tpng', '-o', str(IMG.resolve()),
                        *[str(SALIDA / n) for n in archivos]], check=True)
        print('PNG en', IMG)


if __name__ == '__main__':
    main()
