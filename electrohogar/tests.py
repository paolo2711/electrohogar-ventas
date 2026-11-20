from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse


class InicioDeSesion(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('cargar_demo', stdout=StringIO())

    def test_clave_incorrecta_muestra_el_aviso(self):
        r = self.client.post(reverse('entrar'), {'username': 'mquispe', 'password': 'otra'})
        self.assertContains(r, 'Usuario o clave incorrectos')

    def test_el_gerente_entra_a_las_ventas_del_dia(self):
        r = self.client.post(reverse('entrar'), {'username': 'rdelgado', 'password': 'electrohogar2026'}, follow=True)
        self.assertEqual(r.redirect_chain[-1][0], reverse('ventas:del_dia'))

    def test_sin_rol_se_le_explica_que_pida_uno(self):
        get_user_model().objects.create_user('nuevo', password='x')
        self.client.login(username='nuevo', password='x')
        self.assertContains(self.client.get(reverse('inicio')), 'no tiene un rol asignado')

    def test_sin_sesion_lo_manda_a_entrar(self):
        r = self.client.get(reverse('inicio'))
        self.assertRedirects(r, reverse('entrar') + '?next=/')


class ModeloDeDatos(TestCase):
    def test_el_esquema_documentado_coincide_con_los_modelos(self):
        """Si cambia un modelo, hay que volver a correr docs/diseno/datos.py."""
        import importlib.util
        from pathlib import Path

        ruta = Path(__file__).resolve().parents[1] / 'docs' / 'diseno' / 'datos.py'
        spec = importlib.util.spec_from_file_location('datos', ruta)
        datos = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(datos)
        guardado = (ruta.parent / 'datos' / 'esquema.sql').read_text(encoding='utf-8')
        self.assertEqual(datos.esquema_sql(), guardado, 'esquema.sql está desactualizado: corre docs/diseno/datos.py')


class Estilos(TestCase):
    def test_toda_variable_usada_en_los_estilos_esta_definida(self):
        """Si se borra una variable de base.css, las pruebas no lo notaban (#64)."""
        import re
        from pathlib import Path

        css = Path(__file__).resolve().parents[1] / 'static' / 'css'
        definidas = set(re.findall(r'(--[\w-]+)\s*:', (css / 'base.css').read_text(encoding='utf-8')))
        for archivo in css.glob('*.css'):
            usadas = set(re.findall(r'var\((--[\w-]+)\)', archivo.read_text(encoding='utf-8')))
            self.assertFalse(usadas - definidas, f'{archivo.name} usa variables que no existen')
