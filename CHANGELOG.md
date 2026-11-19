# Registro de cambios

Los cambios de cada versión se anotan aquí. Las versiones siguen el formato `MAYOR.MENOR.PARCHE`.

## [Sin publicar]

## [0.2.1] - 2026-11-18

Corrección encontrada después de publicar la 0.2.0, al correr las simulaciones.

### Corregido

- Al entrar a una pantalla de otro rol se veía una página en blanco que decía "403 Forbidden"; ahora se explica y se ofrece volver a la pantalla propia (#50).

## [0.2.0] - 2026-11-18

Las pantallas propias de los tres roles, el modelo de datos y la integración y entrega continua.

### Agregado

- Workflow de GitHub Actions que revisa la configuración, las migraciones y corre las pruebas en cada push y pull request hacia `develop` y `main`.
- Roles de gerente, cajero y encargado de inventario como grupos de Django, y el comando `cargar_demo` con usuarios y catálogo de prueba.
- Guía de identidad visual (`docs/identidad-visual.md`) y plantilla base de las pantallas.
- Inicio de sesión que lleva a cada rol a su pantalla.
- Pantalla de venta del cajero: búsqueda, venta en curso como hoja de talonario, control de stock al agregar y cobro con F9.
- Pantalla de productos y stock del encargado: filtro de lo que hay que pedir, kárdex de cada producto con su saldo, ingreso de mercadería y ajuste por conteo. El gerente la ve sin poder registrar.
- Menú de la barra según los permisos de cada rol.
- Ventas del día para el gerente: lo cobrado, el cuadre por caja, el detalle de cada venta y la anulación con motivo, que devuelve los productos al stock.
- Modelo de la base de datos en cuatro niveles (conceptual, clases, lógico y físico) y `esquema.sql` de PostgreSQL, generados desde los modelos con `docs/diseno/datos.py`.
- Diagrama de componentes y diagramas de secuencia de inicio de sesión, venta y cobro, ingreso de mercadería y anulación.
- Entrega continua: al crear un tag `v*` se corren las pruebas, se publica la imagen Docker en GitHub Packages y se crea la release (`entrega.yml`). Dockerfile con Gunicorn y WhiteNoise.

### Corregido

- La pantalla de entrada usaba recursos típicos de plantilla (#30).
- La venta guardaba la hora en que se agregó el primer producto en vez de la del cobro, y podía caer en el día anterior en el cuadre (#37).
- El código del producto se partía en dos líneas en la lista completa de Productos y stock (#47).

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
