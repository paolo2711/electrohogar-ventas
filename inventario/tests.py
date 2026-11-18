from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from .models import Categoria, MovimientoStock, Producto
from .roles import CAJERO, rol_de
from .servicios import StockInsuficiente, registrar_movimiento


class MovimientosDeStock(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user('almacen', password='x')
        self.producto = Producto.objects.create(
            codigo='LAV-001', nombre='Lavadora', marca='Samsung', modelo='WA15',
            categoria=Categoria.objects.create(nombre='Lavadoras'),
            precio_venta=Decimal('1499.00'), costo=Decimal('1100.00'), stock_minimo=2,
        )

    def test_un_ingreso_suma_al_stock(self):
        registrar_movimiento(self.producto, MovimientoStock.INGRESO, 5, self.usuario)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, 5)

    def test_no_se_puede_sacar_mas_de_lo_que_hay(self):
        registrar_movimiento(self.producto, MovimientoStock.INGRESO, 1, self.usuario)
        with self.assertRaises(StockInsuficiente):
            registrar_movimiento(self.producto, MovimientoStock.AJUSTE, -2, self.usuario)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, 1)
        self.assertEqual(self.producto.movimientos.count(), 1)

    def test_cada_movimiento_guarda_quien_lo_hizo(self):
        mov = registrar_movimiento(self.producto, MovimientoStock.INGRESO, 3, self.usuario, 'Pedido 145')
        self.assertEqual(mov.usuario, self.usuario)
        self.assertEqual(mov.motivo, 'Pedido 145')

    def test_avisa_cuando_queda_bajo_el_minimo(self):
        registrar_movimiento(self.producto, MovimientoStock.INGRESO, 2, self.usuario)
        self.producto.refresh_from_db()
        self.assertTrue(self.producto.bajo_minimo)


class CargaDeDemo(TestCase):
    def test_carga_roles_usuarios_y_productos_sin_duplicar(self):
        call_command('cargar_demo', stdout=StringIO())
        call_command('cargar_demo', stdout=StringIO())
        self.assertEqual(Producto.objects.count(), 15)
        # La cocina Indurama entra sin stock, así que hay un ingreso menos que productos.
        self.assertEqual(MovimientoStock.objects.count(), 14)
        cajera = get_user_model().objects.get(username='mquispe')
        self.assertEqual(rol_de(cajera), CAJERO)
        self.assertTrue(cajera.has_perm('ventas.add_venta'))
        self.assertFalse(cajera.has_perm('inventario.change_producto'))
