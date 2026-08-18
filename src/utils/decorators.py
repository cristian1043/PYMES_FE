from functools import wraps
from flask import session, flash, redirect, url_for

def requiere_rol(*roles_permitidos):
    """
    Decorador para restringir el acceso a rutas según el rol_id del usuario en la empresa activa.
    - Rol 1: Administrador (acceso total a todas las secciones)
    - Rol 2: Vendedor (Facturas, Clientes, Productos)
    - Rol 3: Almacenista (Compras, Proveedores, Productos)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            usuario = session.get('usuario')
            if not usuario:
                flash("🔒 Acceso Denegado: Debes iniciar sesión con credenciales válidas para acceder a este recurso protegido.", "danger")
                return redirect(url_for('auth.login'))

            # Obtener el rol activo para la empresa actual
            rol_raw = usuario.get('rol_id') or usuario.get('id_rol') or 2
            
            try:
                rol_id = int(rol_raw)
            except (ValueError, TypeError):
                rol_id = 2

            # El Rol 1 (Administrador) siempre tiene acceso a todo en la empresa donde actúa como Admin.
            # Los demás roles sólo acceden a sus rutas permitidas.
            if rol_id == 1 or rol_id in roles_permitidos:
                return f(*args, **kwargs)

            flash("Acceso Denegado: Tu rol en esta empresa no tiene permisos para ingresar a esta sección.", "warning")
            return redirect(url_for('index'))
        return decorated_function
    return decorator
