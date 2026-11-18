# Registro de cambios

Los cambios de cada versión se anotan aquí. Las versiones siguen el formato `MAYOR.MENOR.PARCHE`.

## [Sin publicar]

### Agregado

- Workflow de GitHub Actions que revisa la configuración, las migraciones y corre las pruebas en cada push y pull request hacia `develop` y `main`.
- Roles de gerente, cajero y encargado de inventario como grupos de Django, y el comando `cargar_demo` con usuarios y catálogo de prueba.
- Guía de identidad visual (`docs/identidad-visual.md`) y plantilla base de las pantallas.
- Inicio de sesión que lleva a cada rol a su pantalla.
- Pantalla de venta del cajero: búsqueda, venta en curso como hoja de talonario, control de stock al agregar y cobro con F9.
- Pantalla de productos y stock del encargado: filtro de lo que hay que pedir, kárdex de cada producto con su saldo, ingreso de mercadería y ajuste por conteo. El gerente la ve sin poder registrar.
- Menú de la barra según los permisos de cada rol.
- Ventas del día para el gerente: lo cobrado, el cuadre por caja, el detalle de cada venta y la anulación con motivo, que devuelve los productos al stock.

### Corregido

- La pantalla de entrada usaba recursos típicos de plantilla (#30).
- La venta guardaba la hora en que se agregó el primer producto en vez de la del cobro, y podía caer en el día anterior en el cuadre (#37).
- La paleta se veía demasiado rosada; el acento pasa al azul de la copia del talonario y el papel a un tono más neutro (#39).

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
