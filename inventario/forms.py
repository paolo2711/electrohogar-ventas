from django import forms

from .models import MovimientoStock


class MovimientoForm(forms.Form):
    """Ingreso de mercadería o ajuste por conteo, lo único que el encargado registra a mano."""
    tipo = forms.ChoiceField(choices=[(MovimientoStock.INGRESO, 'Ingreso de mercadería'),
                                      (MovimientoStock.AJUSTE, 'Ajuste por conteo')],
                             initial=MovimientoStock.INGRESO)
    # En un ingreso son las unidades que llegaron; en un ajuste, las que se contaron.
    cantidad = forms.IntegerField(min_value=0, max_value=9999,
                                  error_messages={'required': 'Falta la cantidad.',
                                                  'min_value': 'La cantidad no puede ser negativa.'})
    motivo = forms.CharField(max_length=200, required=False)

    def clean(self):
        datos = super().clean()
        tipo, cantidad = datos.get('tipo'), datos.get('cantidad')
        if tipo == MovimientoStock.INGRESO and cantidad == 0:
            self.add_error('cantidad', 'En un ingreso entra al menos una unidad.')
        if tipo == MovimientoStock.AJUSTE and not datos.get('motivo', '').strip():
            self.add_error('motivo', 'Anota por qué se ajusta, por ejemplo «conteo del sábado».')
        return datos
