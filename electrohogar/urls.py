from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

admin.site.site_header = 'ElectroHogar Ventas'
admin.site.site_title = 'ElectroHogar Ventas'
admin.site.index_title = 'Administración'

urlpatterns = [
    path('admin/', admin.site.urls),
]

# En desarrollo Django sirve también las imágenes subidas.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
