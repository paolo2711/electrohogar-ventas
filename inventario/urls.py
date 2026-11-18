from django.urls import path

from . import views

app_name = 'inventario'

urlpatterns = [
    path('productos/', views.productos, name='productos'),
    path('productos/<int:producto_id>/movimiento/', views.movimiento, name='movimiento'),
]
