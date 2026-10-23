from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from inventario.models import Categoria, MovimientoStock, Producto
from inventario.servicios import StockInsuficiente, registrar_movimiento

from .models import DetalleVenta, Venta
from .servicios import VentaNoValida, anular_venta, confirmar_venta


class ConfirmarYAnular(TestCase):
    def setUp(self):
        usuarios = get_user_model().objects
        self.cajero = usuarios.create_user('caja1', password='x')
        self.gerente = usuarios.create_user('gerente', password='x')
        cat = Categoria.objects.create(nombre='Refrigeradoras')
        self.refri = Producto.objects.create(
            codigo='REF-001', nombre='Refrigeradora', marca='LG', modelo='GT32',
            categoria=cat, precio_venta=Decimal('2199.00'), costo=Decimal('1700.00'), stock_minimo=1,
        )
        self.micro = Producto.objects.create(
            codigo='MIC-001', nombre='Microondas', marca='Samsung', modelo='MS23',
            categoria=cat, precio_venta=Decimal('399.00'), costo=Decimal('280.00'),
        )
        registrar_movimiento(self.refri, MovimientoStock.INGRESO, 2, self.gerente)
        registrar_movimiento(self.micro, MovimientoStock.INGRESO, 5, self.gerente)

    def venta(self, *items):
        v = Venta.objects.create(cajero=self.cajero)
        for producto, cantidad in items:
            DetalleVenta.objects.create(venta=v, producto=producto, cantidad=cantidad,
                                        precio_unitario=producto.precio_venta)
        return v

    def stock(self, producto):
        producto.refresh_from_db()
        return producto.stock_actual

    def test_confirmar_descuenta_el_stock_y_calcula_el_total(self):
        v = confirmar_venta(self.venta((self.refri, 1), (self.micro, 2)), self.cajero)
        self.assertEqual(v.estado, Venta.CONFIRMADA)
        self.assertEqual(v.total, Decimal('2997.00'))
        self.assertEqual(self.stock(self.refri), 1)
        self.assertEqual(self.stock(self.micro), 3)

    def test_si_un_producto_no_alcanza_no_se_descuenta_nada(self):
        # El microondas alcanza, pero la refrigeradora no: no debe quedar ningún descuento.
        v = self.venta((self.micro, 2), (self.refri, 3))
        with self.assertRaises(StockInsuficiente):
            confirmar_venta(v, self.cajero)
        v.refresh_from_db()
        self.assertEqual(v.estado, Venta.REGISTRADA)
        self.assertEqual(self.stock(self.micro), 5)
        self.assertEqual(self.stock(self.refri), 2)

    def test_no_se_confirma_dos_veces(self):
        v = confirmar_venta(self.venta((self.micro, 1)), self.cajero)
        with self.assertRaises(VentaNoValida):
            confirmar_venta(v, self.cajero)
        self.assertEqual(self.stock(self.micro), 4)

    def test_anular_devuelve_el_stock(self):
        v = confirmar_venta(self.venta((self.refri, 2)), self.cajero)
        anular_venta(v, self.gerente, 'El cliente se arrepintió')
        v.refresh_from_db()
        self.assertEqual(v.estado, Venta.ANULADA)
        self.assertEqual(v.anulada_por, self.gerente)
        self.assertEqual(self.stock(self.refri), 2)

    def test_anular_pide_motivo(self):
        v = confirmar_venta(self.venta((self.micro, 1)), self.cajero)
        with self.assertRaises(VentaNoValida):
            anular_venta(v, self.gerente, '')
