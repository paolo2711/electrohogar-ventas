from django.contrib import admin, messages

from .models import Categoria, MovimientoStock, Producto
from .servicios import StockInsuficiente, registrar_movimiento


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    search_fields = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'marca', 'modelo', 'categoria', 'precio_venta',
                    'stock_actual', 'stock_minimo', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['codigo', 'nombre', 'marca', 'modelo']
    readonly_fields = ['stock_actual']


@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'producto', 'tipo', 'cantidad', 'usuario', 'motivo']
    list_filter = ['tipo']
    search_fields = ['producto__nombre', 'producto__codigo', 'motivo']
    autocomplete_fields = ['producto']

    def get_readonly_fields(self, request, obj=None):
        # Un movimiento registrado ya no se cambia: si hubo un error, se corrige con otro.
        return ['producto', 'tipo', 'cantidad', 'motivo'] if obj else []

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        # A mano solo se registran ingresos y ajustes; las ventas los genera el sistema.
        if db_field.name == 'tipo':
            kwargs['choices'] = [c for c in MovimientoStock.TIPOS
                                 if c[0] in (MovimientoStock.INGRESO, MovimientoStock.AJUSTE)]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if change:
            return
        try:
            registrar_movimiento(obj.producto, obj.tipo, obj.cantidad, request.user, obj.motivo)
        except StockInsuficiente as e:
            self.message_user(request, f'No se registró: {e}', messages.ERROR)

    def has_delete_permission(self, request, obj=None):
        return False
