"""Confirmar y anular ventas (casos de uso CU11 y CU12)."""
from django.db import transaction
from django.utils import timezone

from inventario.models import MovimientoStock
from inventario.servicios import registrar_movimiento

from .models import Venta


class VentaNoValida(Exception):
    pass


@transaction.atomic
def confirmar_venta(venta, cajero):
    """Confirma el cobro y descuenta el stock de cada producto en una sola transacción.

    Si un producto no alcanza, registrar_movimiento lanza StockInsuficiente y se
    deshace todo: no queda la venta confirmada ni ningún stock descontado.
    """
    venta = Venta.objects.select_for_update().get(pk=venta.pk)
    if venta.estado != Venta.REGISTRADA:
        raise VentaNoValida(f'{venta} ya está {venta.get_estado_display().lower()}')
    detalles = list(venta.detalles.select_related('producto'))
    if not detalles:
        raise VentaNoValida(f'{venta} no tiene productos')

    for d in detalles:
        registrar_movimiento(d.producto, MovimientoStock.VENTA, -d.cantidad, cajero, f'{venta}')

    venta.total = venta.calcular_total()
    venta.estado = Venta.CONFIRMADA
    # La venta cuenta desde que se cobra, no desde que se agregó el primer producto (#37).
    venta.fecha = timezone.now()
    venta.save(update_fields=['total', 'estado', 'fecha'])
    return venta


@transaction.atomic
def anular_venta(venta, gerente, motivo):
    """Anula una venta confirmada y devuelve las unidades al stock."""
    venta = Venta.objects.select_for_update().get(pk=venta.pk)
    if venta.estado != Venta.CONFIRMADA:
        raise VentaNoValida(f'Solo se anula una venta confirmada; {venta} está {venta.get_estado_display().lower()}')
    if not motivo:
        raise VentaNoValida('Falta el motivo de la anulación')

    for d in venta.detalles.select_related('producto'):
        registrar_movimiento(d.producto, MovimientoStock.ANULACION, d.cantidad, gerente, f'Anulación de {venta}')

    venta.estado = Venta.ANULADA
    venta.anulada_por = gerente
    venta.motivo_anulacion = motivo
    venta.save(update_fields=['estado', 'anulada_por', 'motivo_anulacion'])
    return venta
