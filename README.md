# ElectroHogar Ventas

Sistema web de gestión de ventas para ElectroHogar Delgado, una tienda de electrodomésticos y línea blanca de San Miguel, Lima. La tienda se trabaja como caso de estudio: no existe y sus datos no corresponden a un negocio real.

## Módulos

| Módulo | Qué resuelve |
|---|---|
| Inventario | Descuenta el stock en el momento en que se confirma una venta y avisa cuando un producto baja de su mínimo |
| Ventas y reportes | Registra cada venta y genera reportes por periodo, producto y vendedor |
| Cotizaciones | Guarda las cotizaciones, controla su vigencia y las convierte en venta |
| Pedidos a distancia | Reúne en una bandeja común los pedidos que llegan por teléfono o WhatsApp, con su estado y su responsable |
| Instalaciones y garantías | Agenda las visitas técnicas y conserva el historial de garantías de cada venta |

El acceso es por roles: gerente, vendedor, encargado de almacén, cajera y técnico.

## Tecnología

- Python con Django
- PostgreSQL
- Bootstrap para la interfaz
- Docker para el despliegue

## Flujo de trabajo

El repositorio sigue Gitflow.

| Rama | Para qué |
|---|---|
| `main` | Versiones publicadas. Cada una lleva su tag (`v1.0.0`, `v1.1.0`) |
| `develop` | Integración de lo terminado |
| `feature/*` | Una rama por funcionalidad o entregable, creada desde `develop` |
| `release/*` | Preparación de una versión antes de pasarla a `main` |
| `hotfix/*` | Correcciones urgentes sobre `main` |

Todo cambio entra a `develop` por pull request. Los mensajes de commit van en español y describen qué se hizo.

## Estructura

```
docs/
└── diseno/     Modelo del sistema y diagramas del diseño
```

## Equipo

Grupo 11 del curso Herramientas de Desarrollo, Universidad Tecnológica del Perú, 2026.
