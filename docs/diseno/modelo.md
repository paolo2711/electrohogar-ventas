# Modelo del sistema ElectroHogar Ventas

Este archivo se genera desde `modelo.toml`. Para cambiar algo, se edita ese archivo y se vuelve a correr `generar.py`.

## Actores

| Actor | Descripción |
|---|---|
| Usuario (abstracto) | Cualquier persona del personal con cuenta en el sistema. |
| Gerente | Administra usuarios y roles, consulta todos los reportes y es el único que puede anular una venta. |
| Cajero | Registra la venta, cobra y consulta stock. No modifica productos, precios ni costos. |
| Encargado de inventario | Registra y edita productos con sus imágenes, registra los ingresos de mercadería y ajusta el stock. No vende. |

## Casos de uso: Acceso

| Código | Caso de uso | Actor | Descripción |
|---|---|---|---|
| CU01 | Iniciar sesión | Usuario | Entra con su usuario y contraseña. El sistema le muestra solo lo que su rol permite. |
| CU02 | Gestionar usuarios | Gerente | Crea, edita y desactiva cuentas, y asigna el rol de cada una. |

## Casos de uso: Inventario

| Código | Caso de uso | Actor | Descripción |
|---|---|---|---|
| CU03 | Registrar producto | Encargado de inventario | Da de alta un producto con su categoría, marca, modelo, precio, costo, stock mínimo e imagen. |
| CU04 | Modificar producto | Encargado de inventario | Cambia los datos o la imagen de un producto, o lo desactiva. Un producto con ventas nunca se borra. |
| CU05 | Registrar ingreso de mercadería | Encargado de inventario | Anota la mercadería que llega del proveedor y suma ese stock en el momento. Incluye: CU07 Registrar movimiento de stock. |
| CU06 | Ajustar stock | Encargado de inventario | Corrige el stock cuando el conteo físico no coincide con el sistema. Pide el motivo. Incluye: CU07 Registrar movimiento de stock. |
| CU07 | Registrar movimiento de stock | El sistema | Todo cambio de stock queda como un movimiento con su tipo, cantidad, usuario y fecha. Lo ejecuta el sistema. |
| CU08 | Consultar stock | Gerente, Cajero, Encargado de inventario | Busca un producto y ve cuántas unidades quedan. |
| CU09 | Revisar productos bajo el mínimo | Encargado de inventario | Lista los productos cuyo stock bajó de su mínimo, para pedir reposición. |

## Casos de uso: Ventas y reportes

| Código | Caso de uso | Actor | Descripción |
|---|---|---|---|
| CU10 | Registrar venta | Cajero | Arma la venta con los productos y cantidades. Si un producto no tiene stock suficiente, el sistema no lo deja agregar. |
| CU11 | Confirmar cobro | Cajero | Confirma que el cliente pagó. En la misma operación se descuenta el stock de cada producto. Incluye: CU07 Registrar movimiento de stock. |
| CU12 | Anular venta | Gerente | Anula una venta confirmada y devuelve el stock. Queda registrado quién la anuló y por qué. Incluye: CU07 Registrar movimiento de stock. |
| CU13 | Consultar ventas | Gerente, Cajero | Busca ventas por fecha, número o producto. El cajero ve solo las suyas. |
| CU14 | Generar reporte de ventas | Gerente | Reporte por periodo, por producto y por cajero, con los productos que más se venden. |

## Entidades

### Usuario

Cuenta de una persona del personal.

- nombre
- usuario
- rol: gerente, cajero o inventario
- activo

### Categoria

Familia de productos: refrigeradoras, lavadoras, cocinas, microondas, televisores, pequeños electrodomésticos.

- nombre

### Producto

Un modelo del catálogo.

- codigo
- nombre
- marca
- modelo
- categoria
- precio de venta
- costo
- stock actual
- stock mínimo
- imagen
- activo

### MovimientoStock

Cada entrada o salida de unidades de un producto.

- producto
- tipo: ingreso, ajuste, venta o anulación
- cantidad
- usuario
- fecha y hora
- motivo

### Venta

Una venta hecha en caja.

- numero
- fecha y hora
- cajero
- estado: registrada, confirmada o anulada
- total
- anulada por
- motivo de anulación

### DetalleVenta

Cada producto dentro de una venta.

- venta
- producto
- cantidad
- precio unitario
- subtotal
