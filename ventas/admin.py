from django.contrib import admin, messages

from inventario.servicios import StockInsuficiente

from .models import DetalleVenta, Venta
from .servicios import VentaNoValida, confirmar_venta


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    autocomplete_fields = ['producto']

    def has_change_permission(self, request, obj=None):
        # Una venta confirmada o anulada ya no se toca.
        return obj is None or obj.estado == Venta.REGISTRADA

    has_add_permission = has_change_permission
    has_delete_permission = has_change_permission


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'fecha', 'cajero', 'estado', 'total']
    list_filter = ['estado', 'fecha']
    readonly_fields = ['cajero', 'estado', 'total', 'anulada_por', 'motivo_anulacion']
    inlines = [DetalleVentaInline]
    actions = ['confirmar_cobro']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.cajero = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        # Si el cajero no pone precio, va el precio de venta del producto.
        for d in formset.save(commit=False):
            if not d.precio_unitario:
                d.precio_unitario = d.producto.precio_venta
            d.save()
        formset.save_m2m()
        for d in formset.deleted_objects:
            d.delete()

    @admin.action(description='Confirmar cobro de las ventas seleccionadas')
    def confirmar_cobro(self, request, queryset):
        for venta in queryset:
            try:
                confirmar_venta(venta, request.user)
                self.message_user(request, f'{venta} confirmada.', messages.SUCCESS)
            except (StockInsuficiente, VentaNoValida) as e:
                self.message_user(request, f'{venta} no se confirmó: {e}', messages.ERROR)

    def has_delete_permission(self, request, obj=None):
        return False
