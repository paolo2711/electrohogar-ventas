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
