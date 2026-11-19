from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Categoria, MovimientoStock, Producto
from .roles import CAJERO, rol_de
from .servicios import StockInsuficiente, ajustar_a_conteo, registrar_movimiento


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

    def test_el_ajuste_registra_solo_la_diferencia_con_lo_contado(self):
        registrar_movimiento(self.producto, MovimientoStock.INGRESO, 5, self.usuario)
        mov = ajustar_a_conteo(self.producto, 3, self.usuario, 'Conteo del sábado')
        self.assertEqual(mov.cantidad, -2)
        self.assertIsNone(ajustar_a_conteo(self.producto, 3, self.usuario, 'Otra vez'))


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


class PantallaDeInventario(TestCase):
    """Productos y stock del encargado: filtro por pedir, ingreso y ajuste por conteo."""

    @classmethod
    def setUpTestData(cls):
        call_command('cargar_demo', stdout=StringIO())

    def setUp(self):
        self.client.login(username='jflores', password='electrohogar2026')
        self.cocina = Producto.objects.get(codigo='COC-002')    # agotada
        self.lavadora = Producto.objects.get(codigo='LAV-002')  # 2 unidades, mínimo 2

    def registrar(self, producto, **datos):
        return self.client.post(reverse('inventario:movimiento', args=[producto.pk]), datos, follow=True)

    def stock(self, producto):
        producto.refresh_from_db()
        return producto.stock_actual

    def test_el_encargado_entra_directo_a_productos(self):
        r = self.client.get(reverse('inicio'), follow=True)
        self.assertEqual(r.redirect_chain[-1][0], reverse('inventario:productos'))

    def test_por_pedir_muestra_solo_los_que_llegaron_al_minimo(self):
        r = self.client.get(reverse('inventario:productos'), {'ver': 'pedir'})
        codigos = {p.codigo for p in r.context['productos']}
        self.assertEqual(codigos, {'COC-002', 'REF-003', 'LAV-002', 'PEQ-003'})

    def test_un_ingreso_suma_y_queda_en_el_kardex(self):
        r = self.registrar(self.cocina, tipo='ingreso', cantidad=4, motivo='Guía 001-2231')
        self.assertContains(r, 'Entraron 4')
        self.assertEqual(self.stock(self.cocina), 4)
        self.assertEqual(r.context['kardex'][0]['saldo'], 4)

    def test_un_ajuste_sin_motivo_no_se_registra(self):
        r = self.registrar(self.lavadora, tipo='ajuste', cantidad=1, motivo='')
        self.assertContains(r, 'Anota por qué se ajusta', status_code=400)
        self.assertEqual(self.stock(self.lavadora), 2)

    def test_el_ajuste_deja_el_stock_en_lo_contado(self):
        self.registrar(self.lavadora, tipo='ajuste', cantidad=1, motivo='Una vino golpeada')
        self.assertEqual(self.stock(self.lavadora), 1)
        self.assertEqual(self.lavadora.movimientos.first().cantidad, -1)

    def test_el_gerente_ve_el_stock_pero_no_registra(self):
        self.client.login(username='rdelgado', password='electrohogar2026')
        r = self.client.get(reverse('inventario:productos'), {'p': self.cocina.pk})
        self.assertNotContains(r, 'id="registrar"')
        self.assertEqual(self.registrar(self.cocina, tipo='ingreso', cantidad=4).status_code, 403)

    def test_el_cajero_no_entra(self):
        self.client.login(username='mquispe', password='electrohogar2026')
        r = self.client.get(reverse('inventario:productos'))
        # Ve la página de la tienda con el camino de vuelta, no un 403 en blanco (#50).
        self.assertContains(r, 'no es para tu usuario', status_code=403)
        self.assertContains(r, 'Ir a mi pantalla', status_code=403)
