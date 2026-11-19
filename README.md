# ElectroHogar Ventas

[![Pruebas](https://github.com/paolo2711/electrohogar-ventas/actions/workflows/pruebas.yml/badge.svg?branch=develop)](https://github.com/paolo2711/electrohogar-ventas/actions/workflows/pruebas.yml)

Sistema web de gestión de ventas para ElectroHogar Delgado, una tienda de electrodomésticos y línea blanca de San Miguel, Lima. La tienda se trabaja como caso de estudio: no existe y sus datos no corresponden a un negocio real.

## Módulos

| Módulo | Qué resuelve |
|---|---|
| Inventario | Productos con su imagen, ingresos de mercadería y ajustes. Cada cambio de stock queda registrado con quién lo hizo |
| Ventas y reportes | El stock se descuenta en el momento en que se confirma el cobro, y los reportes salen por periodo, producto y cajero |

Lo usan tres roles: gerente, cajero y encargado de inventario. Los clientes no entran al sistema.

## Tecnología

- Python con Django
- PostgreSQL
- Bootstrap para la interfaz
- Docker para el despliegue

## Cómo correrlo

Con Python 3.12 o superior:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_demo
python manage.py runserver
```

Se entra por `http://127.0.0.1:8000/` y cada usuario cae en la pantalla de su rol. El panel de administración, para crear productos y usuarios, queda en `/admin/`.

`cargar_demo` crea los tres roles, 15 productos de la tienda y un usuario por rol, todos con la clave `electrohogar2026` (solo para la base local):

| Usuario | Rol | Entra a |
|---|---|---|
| `rdelgado` | Gerente | Ventas del día, con anulación |
| `mquispe` | Cajero | Venta |
| `jflores` | Encargado de inventario | Productos y stock |

Sin variables de entorno usa una base SQLite local. Para PostgreSQL se definen `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST` y `POSTGRES_PORT`. En producción también `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0` y `DJANGO_ALLOWED_HOSTS`.

## Entrega continua

Cada versión se publica sola al crear su tag (`git tag v0.2.0 && git push origin v0.2.0`). El workflow `entrega.yml` corre las pruebas, construye la imagen Docker, la sube a GitHub Packages y crea la release con las notas del CHANGELOG.

Para levantar una versión publicada:

```
docker run -p 8000:8000   -e DJANGO_SECRET_KEY=... -e DJANGO_DEBUG=0 -e DJANGO_ALLOWED_HOSTS=localhost   -e POSTGRES_DB=... -e POSTGRES_USER=... -e POSTGRES_PASSWORD=... -e POSTGRES_HOST=...   ghcr.io/paolo2711/electrohogar-ventas:0.2.0
```

Al arrancar aplica las migraciones pendientes.

## Flujo de trabajo

El repositorio sigue Gitflow.

| Rama | Para qué |
|---|---|
| `main` | Versiones publicadas. Cada una lleva su tag (`v1.0.0`, `v1.1.0`) |
| `develop` | Integración de lo terminado |
| `feature/*` | Una rama por funcionalidad o entregable, creada desde `develop` |
| `release/*` | Preparación de una versión antes de pasarla a `main` |
| `hotfix/*` | Correcciones urgentes sobre `main` |

Todo cambio entra a `develop` por pull request, y GitHub Actions corre las pruebas en cada una (`.github/workflows/pruebas.yml`). Si fallan, no se fusiona. Los mensajes de commit van en español y describen qué se hizo.

## Comunicación del equipo

- **Slack**, espacio `electrohogar-ventas`. El canal `#todo-electrohogar-ventas` tiene conectada la app de GitHub, así que avisa solo cuando se abre una tarjeta o una pull request, cuando entra un commit a `main` y cuando se publica una versión.
- **Tablero** en GitHub Projects, con una tarjeta por tarea, su responsable y su prioridad.

## Estructura

```
docs/
└── diseno/
    ├── modelo.toml     Actores, casos de uso y entidades. De aquí sale todo
    ├── procesos.toml   Procesos de negocio: carriles, tareas y flujos
    ├── generar.py      Arma el documento y todos los diagramas
    ├── bpmn.py         Convierte los procesos a BPMN 2.0
    ├── modelo.md       El modelo en tablas, generado
    ├── *.puml, *.bpmn  Diagramas generados
    └── img/            Los diagramas en PNG
```

Los `.bpmn` se pueden abrir y editar en [bpmn.io](https://demo.bpmn.io) o en Camunda Modeler.

Para regenerar todo hacen falta Java, Graphviz y PlantUML para los diagramas UML, y Edge con internet para los BPMN:

```
set PLANTUML_JAR=ruta\a\plantuml.jar
python docs/diseno/generar.py
```

## Equipo

Grupo 11 del curso Herramientas de Desarrollo, Universidad Tecnológica del Perú, 2026.
