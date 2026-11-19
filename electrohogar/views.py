from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import NoReverseMatch, reverse

from inventario.roles import CAJERO, GERENTE, INVENTARIO, rol_de

# Pantalla de entrada de cada rol.
PANTALLA_DE = {
    CAJERO: 'ventas:venta',
    GERENTE: 'ventas:del_dia',
    INVENTARIO: 'inventario:productos',
}


@login_required
def inicio(request):
    rol = rol_de(request.user)
    try:
        return redirect(reverse(PANTALLA_DE[rol]))
    except (KeyError, NoReverseMatch):
        # Sin rol asignado, o con una pantalla que todavía no existe.
        return render(request, 'inicio.html', {'rol': rol})
