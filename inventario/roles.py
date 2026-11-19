"""Los tres roles del sistema como grupos de Django, con los permisos de cada puesto."""
from django.contrib.auth.models import Group, Permission

GERENTE = 'Gerente'
CAJERO = 'Cajero'
INVENTARIO = 'Encargado de inventario'

# app.codename de cada permiso. El cajero no toca productos ni precios, y el
# encargado de inventario no vende (ver docs/diseno/modelo.toml).
PERMISOS = {
    CAJERO: [
        'inventario.view_producto',
        'ventas.add_venta', 'ventas.view_venta',
        'ventas.add_detalleventa', 'ventas.change_detalleventa',
        'ventas.delete_detalleventa', 'ventas.view_detalleventa',
    ],
    INVENTARIO: [
        'inventario.add_producto', 'inventario.change_producto', 'inventario.view_producto',
        'inventario.add_categoria', 'inventario.change_categoria', 'inventario.view_categoria',
        'inventario.add_movimientostock', 'inventario.view_movimientostock',
    ],
    GERENTE: [
        'inventario.view_producto', 'inventario.view_categoria', 'inventario.view_movimientostock',
        'ventas.view_venta', 'ventas.change_venta', 'ventas.view_detalleventa',
        'auth.add_user', 'auth.change_user', 'auth.view_user',
    ],
}


def crear_roles():
    """Crea o actualiza los grupos. Se puede correr las veces que haga falta."""
    for nombre, codigos in PERMISOS.items():
        grupo, _ = Group.objects.get_or_create(name=nombre)
        permisos = []
        for codigo in codigos:
            app, codename = codigo.split('.')
            permisos.append(Permission.objects.get(content_type__app_label=app, codename=codename))
        grupo.permissions.set(permisos)


def rol_de(usuario):
    """Nombre del rol del usuario, o None si no tiene ninguno."""
    nombres = set(usuario.groups.values_list('name', flat=True))
    for rol in (GERENTE, CAJERO, INVENTARIO):
        if rol in nombres:
            return rol
    return None
