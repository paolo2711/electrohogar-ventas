from django.conf import settings
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=60, unique=True)

    class Meta:
        verbose_name = 'categoría'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    codigo = models.CharField('código', max_length=20, unique=True)
    nombre = models.CharField(max_length=120)
    marca = models.CharField(max_length=60)
    modelo = models.CharField(max_length=60)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos',
                                  verbose_name='categoría')
    precio_venta = models.DecimalField('precio de venta', max_digits=10, decimal_places=2)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    # El stock no se edita a mano: cambia solo con un MovimientoStock.
    stock_actual = models.PositiveIntegerField('stock actual', default=0, editable=False)
    stock_minimo = models.PositiveIntegerField('stock mínimo', default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True)
    # Un producto con ventas no se borra, se desactiva.
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} {self.marca} {self.modelo}'

    @property
    def bajo_minimo(self):
        return self.stock_actual <= self.stock_minimo


class MovimientoStock(models.Model):
    INGRESO = 'ingreso'
    AJUSTE = 'ajuste'
    VENTA = 'venta'
    ANULACION = 'anulacion'
    TIPOS = [
        (INGRESO, 'Ingreso de mercadería'),
        (AJUSTE, 'Ajuste por conteo'),
        (VENTA, 'Venta'),
        (ANULACION, 'Anulación de venta'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPOS)
    cantidad = models.IntegerField(help_text='Positiva si entran unidades, negativa si salen.')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, editable=False)
    fecha = models.DateTimeField(auto_now_add=True)
    motivo = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'movimiento de stock'
        verbose_name_plural = 'movimientos de stock'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.get_tipo_display()} {self.cantidad:+d} · {self.producto}'
