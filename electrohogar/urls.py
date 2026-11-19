from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth
from django.urls import include, path

from . import views

admin.site.site_header = 'ElectroHogar Ventas'
admin.site.site_title = 'ElectroHogar Ventas'
admin.site.index_title = 'Administración'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('entrar/', auth.LoginView.as_view(redirect_authenticated_user=True), name='entrar'),
    path('salir/', auth.LogoutView.as_view(), name='salir'),
    path('', include('ventas.urls')),
    path('', include('inventario.urls')),
    path('admin/', admin.site.urls),
]

# En desarrollo Django sirve también las imágenes subidas.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
