# Simulaciones

Escenarios con los que se prueba el sistema como lo usaría cada puesto de la tienda. `simular.py` crea una base SQLite aparte con los datos de `cargar_demo`, recorre los escenarios y guarda cada pantalla; con Microsoft Edge las convierte en PNG.

```
python docs/simulaciones/simular.py [carpeta_de_las_capturas]
```

| N.º | Escenario | Usuario |
|---|---|---|
| E1 | Inicio de sesión correcto e incorrecto | mquispe |
| E2 | Registro de un producto nuevo en Administración | jflores |
| E3 | Ingreso de mercadería y kárdex | jflores |
| E4 | Ajuste por conteo, y el rechazo cuando falta el motivo | jflores |
| E5 | Venta normal y cobro | mquispe |
| E6 | Producto agotado y stock insuficiente | mquispe |
| E7 | Ventas del día, cuadre por caja y anulación | rdelgado |
| E8 | Control de acceso: la cajera no entra a las pantallas de otros | mquispe |

La primera vez que se corrió, el E8 mostró que sin permiso salía un "403 Forbidden" en blanco (#50).
