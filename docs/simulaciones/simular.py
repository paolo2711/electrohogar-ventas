"""Escenarios de simulación del sistema (sección 3.5 del informe).

Uso, desde la raíz del repositorio:
    python docs/simulaciones/simular.py [carpeta_de_las_capturas]

1. Crea una base SQLite aparte (docs/simulaciones/simulacion.sqlite3), aplica las migraciones
   y carga los datos de prueba con cargar_demo. La base de trabajo no se toca.
2. Recorre los escenarios E1 a E8 con el cliente de pruebas de Django, como lo haría cada usuario,
   y guarda el HTML de cada pantalla en docs/simulaciones/salida/.
3. Si encuentra Microsoft Edge, convierte cada pantalla en PNG (1440 x 900).

Los estilos se enlazan desde el disco, así que no hace falta tener el servidor corriendo.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
BASE = AQUI / 'simulacion.sqlite3'
SALIDA = AQUI / 'salida'
EDGE = Path(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe')

if BASE.exists():
    BASE.unlink()
os.environ['DJANGO_SQLITE'] = str(BASE)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'electrohogar.settings')
sys.path.insert(0, str(RAIZ))

import django  # noqa: E402

django.setup()

from django.contrib.staticfiles import finders  # noqa: E402
from django.core.management import call_command  # noqa: E402
from django.test import Client  # noqa: E402
from django.test.utils import setup_test_environment  # noqa: E402

from inventario.models import Categoria, Producto  # noqa: E402
from ventas.models import Venta  # noqa: E402

CLAVE = 'electrohogar2026'
pasos = []


def estaticos_del_disco(html):
    """Cambia /static/... por la ruta del archivo en el disco, para abrir el HTML sin servidor."""
    def cambiar(m):
        ruta = finders.find(m.group(2))
        return f'{m.group(1)}"{Path(ruta).as_uri()}"' if ruta else m.group(0)
    return re.sub(r'((?:href|src)=)"/static/([^"]+)"', cambiar, html)


def guardar(codigo, respuesta, titulo):
    html = estaticos_del_disco(respuesta.content.decode('utf-8'))
    (SALIDA / f'{codigo}.html').write_text(html, encoding='utf-8')
    pasos.append({'codigo': codigo, 'titulo': titulo, 'estado': respuesta.status_code})
    print(f'{codigo} [{respuesta.status_code}] {titulo}')


def entrar(usuario):
    c = Client()
    assert c.login(username=usuario, password=CLAVE), usuario
    return c


def escenarios():
    # E1 Inicio de sesión
    c = Client()
    guardar('E1a', c.get('/entrar/'), 'Formulario de inicio de sesión')
    guardar('E1b', c.post('/entrar/', {'username': 'mquispe', 'password': 'otra'}),
            'Clave incorrecta: el sistema no deja entrar')
    guardar('E1c', c.post('/entrar/', {'username': 'mquispe', 'password': CLAVE}, follow=True),
            'La cajera entra directo a la pantalla de venta')

    # E2 Registro de un producto nuevo, en el panel de administración
    enc = entrar('jflores')
    guardar('E2a', enc.get('/admin/inventario/producto/add/'), 'Formulario de producto nuevo en Administración')
    termas = Categoria.objects.get(nombre='Termas')
    guardar('E2b', enc.post('/admin/inventario/producto/add/', {
        'codigo': 'TER-002', 'nombre': 'Terma a gas 10 L', 'marca': 'Rheem', 'modelo': 'RTG10',
        'categoria': termas.pk, 'precio_venta': '899.00', 'costo': '640.00', 'stock_minimo': '2', 'activo': 'on',
    }, follow=True), 'Producto registrado: aparece en la lista con stock 0')
    terma = Producto.objects.get(codigo='TER-002')

    # E3 Ingreso de mercadería
    url = f'/productos/{terma.pk}/movimiento/?p={terma.pk}'
    guardar('E3a', enc.get(f'/productos/?p={terma.pk}'), 'Kárdex del producto nuevo, sin stock')
    guardar('E3b', enc.post(url, {'tipo': 'ingreso', 'cantidad': '6', 'motivo': 'Guía 002-1187 Rheem'}, follow=True),
            'Ingreso de 6 unidades: el stock y el kárdex se actualizan')

    # E4 Ajuste por conteo
    guardar('E4a', enc.post(url, {'tipo': 'ajuste', 'cantidad': '5', 'motivo': ''}),
            'Ajuste sin motivo: el sistema lo rechaza')
    guardar('E4b', enc.post(url, {'tipo': 'ajuste', 'cantidad': '5', 'motivo': 'Conteo del sábado: una caja golpeada'},
                            follow=True), 'Ajuste por conteo: se registra solo la diferencia')

    # E5 Venta normal
    caja = entrar('mquispe')
    refri = Producto.objects.get(codigo='REF-001')
    micro = Producto.objects.get(codigo='MIC-001')
    licuadora = Producto.objects.get(codigo='PEQ-001')
    guardar('E5a', caja.get('/venta/?q=refrigeradora'), 'Búsqueda de producto en la pantalla de venta')
    for p in (refri, micro, micro):
        caja.post(f'/venta/agregar/{p.pk}/')
    guardar('E5b', caja.get('/venta/?q=microondas'), 'Venta armada en el talonario, con el total')
    guardar('E5c', caja.post('/venta/cobrar/', follow=True), 'Venta cobrada: mensaje con el número y el total')
    venta = Venta.objects.filter(estado=Venta.CONFIRMADA).latest('pk')
    # Una segunda venta del día, para que el resumen del gerente tenga más de una.
    caja.post(f'/venta/agregar/{licuadora.pk}/')
    caja.post('/venta/cobrar/')

    # E6 Agotado y stock insuficiente
    guardar('E6a', caja.get('/venta/?q=cocina'), 'Producto agotado: no se puede agregar')
    mabe = Producto.objects.get(codigo='REF-003')
    for _ in range(mabe.stock_actual):
        caja.post(f'/venta/agregar/{mabe.pk}/')
    guardar('E6b', caja.post(f'/venta/agregar/{mabe.pk}/', {'q': 'mabe'}, follow=True),
            'Se piden más unidades de las que hay: el sistema avisa y no las agrega')

    # E7 Ventas del día y anulación
    ger = entrar('rdelgado')
    guardar('E7a', ger.get('/ventas/'), 'Ventas del día con lo cobrado y el cuadre por caja')
    guardar('E7b', ger.get(f'/ventas/?v={venta.pk}'), 'Detalle de la venta elegida')
    guardar('E7c', ger.post(f'/ventas/{venta.pk}/anular/', {'motivo': 'El cliente cambió de modelo en tienda'},
                            follow=True), 'Venta anulada: sale del total y el stock vuelve')

    # E8 Control de acceso
    guardar('E8a', caja.get('/productos/'), 'La cajera no puede entrar a Productos y stock')
    guardar('E8b', caja.get('/ventas/'), 'Ni a las ventas del día')


def capturar(destino):
    if not EDGE.exists():
        print('Sin Edge: quedan solo los HTML en', SALIDA)
        return
    destino.mkdir(parents=True, exist_ok=True)
    for p in pasos:
        titulo = re.sub(r'[:/?]', '', p['titulo']).replace('  ', ' ')
        png = destino / f"3.5.3 - {p['codigo']} {titulo}.png"
        subprocess.run([str(EDGE), '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1440,900',
                        '--blink-settings=preferredColorScheme=1',  # tema claro también en el admin
                        '--virtual-time-budget=5000', f'--screenshot={png}', (SALIDA / f"{p['codigo']}.html").as_uri()],
                       capture_output=True, timeout=120)
    print('Capturas en', destino)


if __name__ == '__main__':
    SALIDA.mkdir(exist_ok=True)
    for f in SALIDA.glob('*'):
        f.unlink()
    call_command('migrate', verbosity=0)
    call_command('cargar_demo', verbosity=0)
    setup_test_environment()  # deja usar el cliente de pruebas fuera de una prueba
    escenarios()
    (SALIDA / 'pasos.json').write_text(json.dumps(pasos, ensure_ascii=False, indent=1), encoding='utf-8')
    capturar(Path(sys.argv[1]) if len(sys.argv) > 1 else SALIDA)
