"""Toda modificación del stock pasa por aquí (caso de uso CU07)."""
from django.db import transaction

from .models import MovimientoStock, Producto


class StockInsuficiente(Exception):
    def __init__(self, producto, disponible, pedido):
        self.producto = producto
        super().__init__(f'{producto}: hay {disponible} y se piden {pedido}')


@transaction.atomic
def registrar_movimiento(producto, tipo, cantidad, usuario, motivo=''):
    """Suma o resta unidades y deja el movimiento registrado con su autor.

    Bloquea la fila del producto hasta que termina la transacción, para que dos
    cajas no descuenten la misma unidad a la vez.
    """
    producto = Producto.objects.select_for_update().get(pk=producto.pk)
    nuevo = producto.stock_actual + cantidad
    if nuevo < 0:
        raise StockInsuficiente(producto, producto.stock_actual, -cantidad)
    producto.stock_actual = nuevo
    producto.save(update_fields=['stock_actual'])
    return MovimientoStock.objects.create(
        producto=producto, tipo=tipo, cantidad=cantidad, usuario=usuario, motivo=motivo,
    )
