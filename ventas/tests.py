from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

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


class PantallaDeVenta(TestCase):
    """La pantalla del cajero: agregar, quitar y cobrar desde el navegador."""

    @classmethod
    def setUpTestData(cls):
        from io import StringIO

        from django.core.management import call_command
        call_command('cargar_demo', stdout=StringIO())

    def setUp(self):
        self.client.login(username='mquispe', password='electrohogar2026')
        self.refri = Producto.objects.get(codigo='REF-003')     # le queda 1 unidad
        self.licuadora = Producto.objects.get(codigo='PEQ-001')  # le quedan 12

    def agregar(self, producto):
        return self.client.post(reverse('ventas:agregar', args=[producto.pk]), follow=True)

    def stock(self, producto):
        producto.refresh_from_db()
        return producto.stock_actual

    def test_el_cajero_entra_directo_a_la_venta(self):
        r = self.client.get(reverse('inicio'), follow=True)
        self.assertEqual(r.redirect_chain[-1][0], reverse('ventas:venta'))

    def test_el_encargado_de_inventario_no_puede_vender(self):
        self.client.login(username='jflores', password='electrohogar2026')
        self.assertNotEqual(self.client.get(reverse('ventas:venta')).status_code, 200)

    def test_no_deja_agregar_mas_de_lo_que_hay(self):
        self.agregar(self.refri)
        r = self.agregar(self.refri)
        self.assertContains(r, 'No alcanza el stock')
        self.assertEqual(DetalleVenta.objects.get(producto=self.refri).cantidad, 1)

    def test_quitar_resta_de_a_uno_y_luego_saca_el_producto(self):
        self.agregar(self.licuadora)
        self.agregar(self.licuadora)
        detalle = DetalleVenta.objects.get(producto=self.licuadora)
        self.client.post(reverse('ventas:quitar', args=[detalle.pk]))
        detalle.refresh_from_db()
        self.assertEqual(detalle.cantidad, 1)
        self.client.post(reverse('ventas:quitar', args=[detalle.pk]))
        self.assertFalse(DetalleVenta.objects.filter(pk=detalle.pk).exists())

    def test_cobrar_confirma_la_venta_y_descuenta_el_stock(self):
        self.agregar(self.licuadora)
        self.agregar(self.licuadora)
        r = self.client.post(reverse('ventas:cobrar'), follow=True)
        self.assertContains(r, 'cobrada por S/')
        venta = Venta.objects.get()
        self.assertEqual(venta.estado, Venta.CONFIRMADA)
        self.assertEqual(venta.total, Decimal('378.00'))
        self.assertEqual(self.stock(self.licuadora), 10)
        # La siguiente venta empieza de cero.
        self.assertContains(self.client.get(reverse('ventas:venta')), 'Venta nueva')

    def test_si_otra_caja_se_llevo_la_ultima_unidad_no_se_cobra(self):
        self.agregar(self.refri)
        otra_caja = get_user_model().objects.get(username='rdelgado')
        registrar_movimiento(self.refri, MovimientoStock.VENTA, -1, otra_caja)
        r = self.client.post(reverse('ventas:cobrar'), follow=True)
        self.assertContains(r, 'No se cobró')
        self.assertEqual(Venta.objects.get().estado, Venta.REGISTRADA)
