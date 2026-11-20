# Identidad visual de ElectroHogar Ventas

Todas las pantallas se arman con lo que dice este archivo. Si una pantalla necesita algo que aquí no está, primero se agrega aquí y después se usa.

## Personalidad: el mostrador de confianza

ElectroHogar Delgado es una tienda familiar de un solo local en San Miguel, abierta en 2013. Hoy vende con lista de precios impresa y talonario. El sistema tiene que sentirse como esa misma tienda, ordenada, y no como un programa genérico.

Cuatro rasgos, y lo que cada uno decide:

| Rasgo | Qué significa en pantalla |
|---|---|
| **Cercano** | Fondo color papel en vez de blanco, textos en castellano llano ("No alcanza el stock", no "Error 409") |
| **Directo** | Una sola acción principal por pantalla, con el único color fuerte. Nada de íconos decorativos |
| **Ordenado** | Todo alineado a una grilla, cifras en columnas, separadores finos como los renglones del talonario |
| **Ágil** | Quien la usa es un cajero con el cliente delante: búsqueda con teclado, precios grandes, botones de 48 px o más |

## Referencias

- **El talonario y la boleta.** El panel de la venta se dibuja como una hoja de talonario: papel, renglones punteados y el total al pie, separado por una línea de tinta. El color de acento es el azul de la copia en papel carbón del talonario y se usa solo en el botón principal.
- **La tarjeta de kárdex.** El control de existencias que llevan a mano muchas tiendas en el Perú: entradas, salidas y saldo en columnas. En la pantalla del encargado, la ficha de cada producto sigue ese formato, y es la única caja de esa pantalla.
- **Square Point of Sale.** En su rediseño de 2026 la venta en curso queda siempre visible junto a la lista de productos, para armar el pedido con menos pasos ([notas de versión de Square](https://squareup.com/us/en/release-notes/release-notes-september-10th)). Tomamos esa distribución: productos a la izquierda, venta a la derecha.
- **Atkinson Hyperlegible.** Tipografía del Braille Institute pensada para que cada letra se distinga de las demás, incluso con poca vista o con prisa. Es libre (SIL OFL 1.1) y tiene versión monoespaciada para cifras y códigos ([Braille Institute](https://www.brailleinstitute.org/freefont/)).

## Colores

Se usan solo estas variables (en `static/css/base.css`). Ningún color se escribe suelto en una plantilla.

| Variable | Valor | Uso |
|---|---|---|
| `--papel` | `#F1F3F5` | Fondo de la página |
| `--hoja` | `#FAFBFC` | Paneles y tablas, como una hoja sobre el mostrador |
| `--renglon` | `#D5DBE1` | Bordes y separadores |
| `--tinta` | `#221E19` | Texto principal |
| `--tinta-suave` | `#6A6158` | Texto secundario, etiquetas |
| `--sello` | `#1F4E8C` | Acción principal y lo que hay que mirar primero. Solo uno por pantalla |
| `--sello-oscuro` | `#173B6B` | El mismo botón al pasar el mouse o al presionarlo |
| `--sello-claro` | `#DCE6F3` | Fondo de la fila seleccionada |
| `--bien` | `#2E6B45` | Confirmaciones ("Venta confirmada") |
| `--aviso` | `#8A6414` | Stock bajo el mínimo |
| `--falla` | `#9B2C2C` | Errores y stock insuficiente |

Los estados se dicen con texto y, si hace falta, con el color del texto. No se usan píldoras de colores ni el semáforo verde, amarillo y rojo.

Contraste comprobado: `--tinta` y `--tinta-suave` sobre `--papel` superan 4,5:1, y el texto blanco sobre `--sello` también.

## Tipografía

| Para | Letra | Tamaño |
|---|---|---|
| Textos, botones, títulos | Atkinson Hyperlegible Next | 16 px el cuerpo; títulos 20 y 28 px en peso 700 |
| Precios, cantidades, códigos de producto, números de venta | Atkinson Hyperlegible Mono | 16 px en tablas; el total de la venta 40 px |

Las cifras siempre alineadas a la derecha y con dos decimales: `S/ 2 199.00`.

## Espacio y forma

- Base de 4 px. Espacios permitidos: 4, 8, 12, 16, 24, 32, 48.
- Esquinas de 3 px, casi rectas, como el papel.
- Bordes de 1 px en `--renglon` en vez de sombras. La única sombra es el anillo de foco del teclado.
- Botones y filas clicables de 48 px de alto como mínimo; el botón principal, 56 px.

## Teclado

| Tecla | Qué hace |
|---|---|
| `/` | Lleva el cursor a la búsqueda |
| `Enter` en la búsqueda | Agrega a la venta el primer producto encontrado |
| `F9` | Confirma el cobro |

Los atajos se muestran al lado del botón que reemplazan.

## Lo que no va

Son los recursos que más delatan una interfaz hecha con plantilla o generada automáticamente. Los sacamos de un catálogo de esos patrones ([Wystack, anti-patterns](https://cdn.jsdelivr.net/npm/@wystack/agent-kit@0.12.0/wystack-agent-kit/references/anti-patterns.md)) y de la revisión de la primera pantalla (issue #30).

- **Borde grueso de color en un solo lado** de una caja, arriba o a la izquierda. Para separar se usan líneas finas completas en `--renglon` o `--tinta`.
- **El nombre de la tienda en dos colores.** Va entero en `--tinta`.
- **Todo centrado.** Las pantallas se alinean a la izquierda; centrar solo cuando de verdad hay una sola cosa que mirar.
- **Todo dentro de tarjetas**, y menos aún tarjetas dentro de tarjetas. Un formulario va directo sobre el papel. La única caja de la pantalla de venta es el talonario, porque representa una hoja.
- **Blanco o negro puros.** El texto sobre el sello va en `--hoja`, y el texto oscuro es `--tinta`.
- **Todos los botones como principales.** Uno por pantalla.
- **Mensajes en caja con barra de color.** Un mensaje es una frase en el color de su estado.
- **La letra monoespaciada como adorno "técnico".** Aquí se usa solo para cifras y códigos, donde alinea columnas.
- Degradados, brillos, vidrio esmerilado, sombras grandes, emojis, ilustraciones, íconos encima de cada título, esquinas muy redondeadas, píldoras de colores y animaciones que no informen algo.
- Textos genéricos: "Aceptar", "Enviar", "Algo salió mal". Cada botón dice lo que hace ("Cobrar", "Entrar") y cada error dice qué pasó y qué hacer.
