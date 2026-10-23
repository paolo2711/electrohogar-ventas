from decimal import Decimal

from django.conf import settings
from django.db import models


class Venta(models.Model):
    REGISTRADA = 'registrada'
    CONFIRMADA = 'confirmada'
    ANULADA = 'anulada'
    ESTADOS = [
        (REGISTRADA, 'Registrada'),
        (CONFIRMADA, 'Confirmada'),
        (ANULADA, 'Anulada'),
    ]

    fecha = models.DateTimeField(auto_now_add=True)
    cajero = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                               related_name='ventas', editable=False)
    estado = models.CharField(max_length=10, choices=ESTADOS, default=REGISTRADA, editable=False)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'), editable=False)
    anulada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                    related_name='ventas_anuladas', null=True, blank=True, editable=False)
    motivo_anulacion = models.CharField('motivo de anulación', max_length=200, blank=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'Venta {self.pk}'

    def calcular_total(self):
        return sum((d.subtotal for d in self.detalles.all()), Decimal('0'))


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    # Viene de la app de inventario.
    producto = models.ForeignKey('inventario.Producto', on_delete=models.PROTECT, related_name='ventas')
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField('precio unitario', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'detalle de venta'
        verbose_name_plural = 'detalles de venta'

    def __str__(self):
        return f'{self.cantidad} × {self.producto}'

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
