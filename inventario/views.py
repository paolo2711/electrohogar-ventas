"""Productos y stock del encargado de inventario (casos de uso CU05 a CU07)."""
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import MovimientoForm
from .models import MovimientoStock, Producto
from .servicios import ajustar_a_conteo, registrar_movimiento

POR_PEDIR = Q(stock_actual__lte=F('stock_minimo'))
# Nombre corto de cada movimiento para la columna angosta del kárdex.
CORTO = {MovimientoStock.INGRESO: 'Ingreso', MovimientoStock.AJUSTE: 'Ajuste',
         MovimientoStock.VENTA: 'Venta', MovimientoStock.ANULACION: 'Anulación'}


def kardex(producto, cuantos=15):
    """Últimos movimientos del producto con el saldo que quedó después de cada uno."""
    saldo = producto.stock_actual
    filas = []
    for m in producto.movimientos.select_related('usuario')[:cuantos]:
        filas.append({'mov': m, 'que': CORTO[m.tipo], 'saldo': saldo})
        saldo -= m.cantidad
    return filas


def pantalla(request, producto=None, form=None, status=200):
    q = request.GET.get('q', '').strip()
    ver = request.GET.get('ver', '')
    activos = Producto.objects.filter(activo=True)
    lista = activos.select_related('categoria')
    if ver == 'pedir':
        lista = lista.filter(POR_PEDIR)
    if q:
        lista = lista.filter(Q(codigo__icontains=q) | Q(nombre__icontains=q) |
                             Q(marca__icontains=q) | Q(modelo__icontains=q))
    if producto is None and request.GET.get('p', '').isdigit():
        producto = activos.filter(pk=request.GET['p']).first()
    return render(request, 'inventario/productos.html', {
        'q': q, 'ver': ver,
        'productos': lista.order_by('codigo'),
        'total_activos': activos.count(),
        'total_por_pedir': activos.filter(POR_PEDIR).count(),
        'producto': producto,
        'kardex': kardex(producto) if producto else [],
        'form': form or MovimientoForm(),
        'puede_registrar': request.user.has_perm('inventario.add_movimientostock'),
    }, status=status)


@permission_required('inventario.view_movimientostock', raise_exception=True)
def productos(request):
    return pantalla(request)


@require_POST
@permission_required('inventario.add_movimientostock', raise_exception=True)
def movimiento(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id, activo=True)
    form = MovimientoForm(request.POST)
    if not form.is_valid():
        return pantalla(request, producto, form, status=400)

    tipo, cantidad = form.cleaned_data['tipo'], form.cleaned_data['cantidad']
    motivo = form.cleaned_data['motivo'].strip()
    antes = producto.stock_actual
    if tipo == MovimientoStock.INGRESO:
        registrar_movimiento(producto, tipo, cantidad, request.user, motivo)
        messages.success(request, f'Entraron {cantidad} de {producto}. Ahora hay {antes + cantidad}.')
    elif ajustar_a_conteo(producto, cantidad, request.user, motivo):
        messages.success(request, f'Ajustado {producto}: el sistema tenía {antes} y se contaron {cantidad}.')
    else:
        messages.warning(request, f'El conteo de {producto} coincide con el sistema; no se registró nada.')

    filtros = {k: v for k, v in (('q', request.GET.get('q', '')), ('ver', request.GET.get('ver', ''))) if v}
    return redirect(reverse('inventario:productos') + '?' + urlencode({**filtros, 'p': producto.pk}))
