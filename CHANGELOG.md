# Registro de cambios

Los cambios de cada versión se anotan aquí. Las versiones siguen el formato `MAYOR.MENOR.PARCHE`.

## [Sin publicar]

### Agregado

- Workflow de GitHub Actions que revisa la configuración, las migraciones y corre las pruebas en cada push y pull request hacia `develop` y `main`.

## [0.1.0] - 2026-10-22

Primera versión: el diseño del sistema y la base del proyecto. Todavía no hay pantallas propias; se usa el panel de administración de Django.

### Agregado

- Estructura inicial del repositorio, con README, `.gitignore` y la carpeta del diseño.
- Modelo del sistema en `docs/diseno/modelo.toml`: tres actores, catorce casos de uso en tres módulos y seis entidades.
- Script que genera el documento del modelo.
- Diagrama general de casos de uso.
- Proceso de venta en tienda en BPMN 2.0, el actual y el que usa el sistema.
- Diagrama de actividades de confirmar el cobro y descontar el stock, con los casos de stock insuficiente y de falla a la mitad.
- Proyecto Django con las apps de inventario y ventas. El stock solo cambia por movimientos registrados, y confirmar una venta descuenta todo o nada.
