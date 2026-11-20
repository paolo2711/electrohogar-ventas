"""Pantallas de ventas: la venta del cajero (CU10 y CU11) y las ventas del día del gerente (CU12)."""
from datetime import date, timedelta
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from inventario.models import Producto
from inventario.servicios import StockInsuficiente

from .models import DetalleVenta, Venta
from .servicios import VentaNoValida, anular_venta, confirmar_venta
from .templatetags.caja import soles

CLAVE = 'venta_en_curso'


def venta_en_curso(request, crear=False):
    """La venta registrada que el cajero está armando, guardada en su sesión."""
    venta = Venta.objects.filter(pk=request.session.get(CLAVE), cajero=request.user,
                                 estado=Venta.REGISTRADA).first()
    if venta is None and crear:
        venta = Venta.objects.create(cajero=request.user)
        request.session[CLAVE] = venta.pk
    return venta


@permission_required('ventas.add_venta')
def venta(request):
    q = request.GET.get('q', '').strip()
    productos = Producto.objects.filter(activo=True).select_related('categoria')
    if q:
        productos = productos.filter(Q(codigo__icontains=q) | Q(nombre__icontains=q) |
                                     Q(marca__icontains=q) | Q(modelo__icontains=q))
    actual = venta_en_curso(request)
    detalles = list(actual.detalles.select_related('producto')) if actual else []
    return render(request, 'ventas/venta.html', {
        'q': q,
        'productos': productos[:20],
        'venta': actual,
        'detalles': detalles,
        'total': sum((d.subtotal for d in detalles), 0),
        'unidades': sum(d.cantidad for d in detalles),
    })


@require_POST
@permission_required('ventas.add_venta')
def agregar(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id, activo=True)
    actual = venta_en_curso(request, crear=True)
    detalle = actual.detalles.filter(producto=producto).first()
    pedidas = (detalle.cantidad if detalle else 0) + 1
    if pedidas > producto.stock_actual:
        messages.error(request, f'No alcanza el stock: de {producto} quedan {producto.stock_actual}.')
    elif detalle:
        detalle.cantidad = pedidas
        detalle.save(update_fields=['cantidad'])
    else:
        DetalleVenta.objects.create(venta=actual, producto=producto, cantidad=1,
                                    precio_unitario=producto.precio_venta)
    return redirect_a_venta(request)


@require_POST
@permission_required('ventas.add_venta')
def quitar(request, detalle_id):
    """Resta una unidad; si era la última, saca el producto de la venta."""
    actual = venta_en_curso(request)
    detalle = get_object_or_404(DetalleVenta, pk=detalle_id, venta=actual)
    if detalle.cantidad > 1 and request.POST.get('todo') != '1':
        detalle.cantidad -= 1
        detalle.save(update_fields=['cantidad'])
    else:
        detalle.delete()
    return redirect_a_venta(request)


@require_POST
@permission_required('ventas.add_venta')
def cobrar(request):
    actual = venta_en_curso(request)
    if actual is None:
        messages.error(request, 'No hay productos en la venta.')
        return redirect('ventas:venta')
    try:
        cobrada = confirmar_venta(actual, request.user)
    except StockInsuficiente as e:
        messages.error(request, f'No se cobró: de {e.producto} ya no alcanza el stock. Quítalo o baja la cantidad.')
    except VentaNoValida as e:
        messages.error(request, f'No se cobró: {e}.')
    else:
        del request.session[CLAVE]
        messages.success(request, f'Venta {cobrada.pk:04d} cobrada por {soles(cobrada.total)}. Ya puedes emitir la boleta.')
    return redirect('ventas:venta')


def redirect_a_venta(request):
    """Vuelve a la venta conservando la búsqueda que tenía el cajero."""
    q = request.POST.get('q', '')
    return redirect(reverse('ventas:venta') + (f'?{urlencode({"q": q})}' if q else ''))


def dia_pedido(request):
    """El día que pidió ver el gerente (?dia=AAAA-MM-DD), o hoy."""
    try:
        return date.fromisoformat(request.GET.get('dia', ''))
    except ValueError:
        return timezone.localdate()


@permission_required('ventas.change_venta', raise_exception=True)
def del_dia(request):
    dia = dia_pedido(request)
    del_dia = Venta.objects.filter(fecha__date=dia, estado__in=[Venta.CONFIRMADA, Venta.ANULADA])
    ventas = del_dia.select_related('cajero').annotate(unidades=Sum('detalles__cantidad'))
    cobradas = del_dia.filter(estado=Venta.CONFIRMADA)
    elegida = del_dia.select_related('cajero', 'anulada_por').filter(pk=request.GET.get('v')).first() if request.GET.get('v', '').isdigit() else None
    return render(request, 'ventas/del_dia.html', {
        'dia': dia,
        'hoy': timezone.localdate(),
        'anterior': dia - timedelta(days=1),
        'siguiente': dia + timedelta(days=1),
        'ventas': ventas,
        'cobrado': cobradas.aggregate(t=Sum('total'))['t'] or 0,
        'cuantas': cobradas.count(),
        'anuladas': del_dia.filter(estado=Venta.ANULADA).aggregate(n=Count('id'), t=Sum('total')),
        # Para el cuadre de caja: lo que cobró cada cajero.
        'por_caja': cobradas.values('cajero__first_name', 'cajero__username')
                            .annotate(n=Count('id'), t=Sum('total')).order_by('-t'),
        # Qué se llevó la gente ese día: lo más vendido primero (#62). Las anuladas no entran.
        'por_producto': DetalleVenta.objects.filter(venta__in=cobradas)
                                    .values('producto__nombre', 'producto__marca', 'producto__modelo')
                                    .annotate(unidades=Sum('cantidad'),
                                              importe=Sum(ExpressionWrapper(
                                                  F('cantidad') * F('precio_unitario'),
                                                  output_field=DecimalField(max_digits=12, decimal_places=2))))
                                    .order_by('-unidades', '-importe'),
        'elegida': elegida,
        'detalles': elegida.detalles.select_related('producto') if elegida else [],
    })


@require_POST
@permission_required('ventas.change_venta', raise_exception=True)
def anular(request, venta_id):
    venta = get_object_or_404(Venta, pk=venta_id)
    motivo = request.POST.get('motivo', '').strip()
    try:
        anular_venta(venta, request.user, motivo)
    except VentaNoValida as e:
        messages.error(request, f'No se anuló: {e}.')
    else:
        messages.success(request, f'Venta {venta.pk:04d} anulada. Los productos volvieron al stock.')
    dia = timezone.localtime(venta.fecha).date()
    return redirect(reverse('ventas:del_dia') + '?' + urlencode({'dia': dia.isoformat(), 'v': venta.pk}))
