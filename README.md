# ElectroHogar Ventas

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
└── diseno/
    ├── modelo.toml    Actores, casos de uso y entidades. De aquí sale todo
    ├── generar.py     Arma el documento y los diagramas
    └── modelo.md      El modelo en tablas, generado
```

## Equipo

Grupo 11 del curso Herramientas de Desarrollo, Universidad Tecnológica del Perú, 2026.
