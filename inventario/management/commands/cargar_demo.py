"""Carga los roles, tres usuarios y el catálogo de prueba de la tienda.

    python manage.py cargar_demo

Se puede correr más de una vez: lo que ya existe no se duplica.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

from inventario.models import Categoria, MovimientoStock, Producto
from inventario.roles import CAJERO, GERENTE, INVENTARIO, crear_roles
from inventario.servicios import registrar_movimiento

# Solo para la base local de prueba. En producción los usuarios se crean a mano.
CLAVE_DEMO = 'electrohogar2026'

USUARIOS = [
    ('rdelgado', 'Ricardo', 'Delgado', GERENTE),
    ('mquispe', 'María', 'Quispe', CAJERO),
    ('jflores', 'Jorge', 'Flores', INVENTARIO),
]

# código, nombre, marca, modelo, categoría, precio, costo, stock inicial, stock mínimo
CATALOGO = [
    ('REF-001', 'Refrigeradora', 'LG', 'GT32WPG', 'Refrigeradoras', '2199.00', '1720.00', 4, 2),
    ('REF-002', 'Refrigeradora', 'Samsung', 'RT38K5930SL', 'Refrigeradoras', '2599.00', '2050.00', 3, 2),
    ('REF-003', 'Refrigeradora', 'Mabe', 'RMA250PVPE', 'Refrigeradoras', '1499.00', '1150.00', 1, 2),
    ('LAV-001', 'Lavadora', 'LG', 'WT13DPBK', 'Lavadoras', '1799.00', '1390.00', 5, 2),
    ('LAV-002', 'Lavadora', 'Samsung', 'WA17T6260BV', 'Lavadoras', '1999.00', '1560.00', 2, 2),
    ('COC-001', 'Cocina 4 hornillas', 'Mabe', 'EMP6120PG0', 'Cocinas', '899.00', '680.00', 6, 2),
    ('COC-002', 'Cocina 5 hornillas', 'Indurama', 'Bari Plus', 'Cocinas', '1099.00', '830.00', 0, 1),
    ('MIC-001', 'Microondas 23 L', 'Samsung', 'MS23K3513AS', 'Microondas', '399.00', '280.00', 8, 3),
    ('MIC-002', 'Microondas 20 L', 'Oster', 'POGYMB2702', 'Microondas', '329.00', '230.00', 5, 3),
    ('TV-001', 'Televisor 55 pulgadas UHD', 'LG', '55UR7300', 'Televisores', '2299.00', '1800.00', 3, 1),
    ('TV-002', 'Televisor 50 pulgadas UHD', 'Samsung', 'UN50CU7000', 'Televisores', '1899.00', '1480.00', 4, 1),
    ('PEQ-001', 'Licuadora 1,5 L', 'Oster', 'BLSTMB', 'Pequeños electrodomésticos', '189.00', '120.00', 12, 4),
    ('PEQ-002', 'Plancha a vapor', 'Philips', 'GC1905', 'Pequeños electrodomésticos', '99.00', '62.00', 10, 4),
    ('PEQ-003', 'Aspiradora', 'Electrolux', 'ABS01', 'Pequeños electrodomésticos', '449.00', '320.00', 2, 2),
    ('TER-001', 'Terma eléctrica 50 L', 'Sole', 'SOLTE050', 'Termas', '649.00', '470.00', 3, 1),
]


class Command(BaseCommand):
    help = 'Carga roles, usuarios y productos de prueba.'

    @transaction.atomic
    def handle(self, *args, **opciones):
        crear_roles()
        usuarios = get_user_model().objects
        for usuario, nombre, apellido, rol in USUARIOS:
            u, nuevo = usuarios.get_or_create(username=usuario, defaults={'first_name': nombre, 'last_name': apellido})
            if nuevo:
                u.set_password(CLAVE_DEMO)
            # Gerente y encargado usan también el panel de administración de Django,
            # hasta que sus pantallas propias estén listas.
            u.is_staff = rol in (GERENTE, INVENTARIO)
            u.save()
            u.groups.set([Group.objects.get(name=rol)])
        encargado = usuarios.get(username='jflores')

        nuevos = 0
        for codigo, nombre, marca, modelo, cat, precio, costo, stock, minimo in CATALOGO:
            categoria, _ = Categoria.objects.get_or_create(nombre=cat)
            producto, creado = Producto.objects.get_or_create(codigo=codigo, defaults={
                'nombre': nombre, 'marca': marca, 'modelo': modelo, 'categoria': categoria,
                'precio_venta': Decimal(precio), 'costo': Decimal(costo), 'stock_minimo': minimo,
            })
            if creado:
                nuevos += 1
                if stock:
                    registrar_movimiento(producto, MovimientoStock.INGRESO, stock, encargado, 'Inventario inicial')
        self.stdout.write(f'Roles y usuarios listos. Productos nuevos: {nuevos} de {len(CATALOGO)}.')
