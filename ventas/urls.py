from django.urls import path

from . import views

app_name = 'ventas'

urlpatterns = [
    path('venta/', views.venta, name='venta'),
    path('venta/agregar/<int:producto_id>/', views.agregar, name='agregar'),
    path('venta/quitar/<int:detalle_id>/', views.quitar, name='quitar'),
    path('venta/cobrar/', views.cobrar, name='cobrar'),
    path('ventas/', views.del_dia, name='del_dia'),
    path('ventas/<int:venta_id>/anular/', views.anular, name='anular'),
]
