from functools import wraps
from flask import session, flash, redirect, url_for

def requiere_rol(*roles_permitidos):
    """
    Decorador para restringir el acceso a rutas según el rol_id del usuario autenticado.
    - Rol 1: Administrador (acceso a todo)
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
            
            empresa_activa = session.get('empresa_activa', {})
            rol_raw = usuario.get('id_rol') or usuario.get('rol_id') or empresa_activa.get('rol_id') or 1
            
            try:
                rol_id = int(rol_raw)
            except (ValueError, TypeError):
                rol_id = 1 if str(rol_raw).lower() in ['1', 'admin', 'administrador'] else 2

            # El Rol 1 (Administrador) siempre tiene acceso maestro a todo
            if rol_id == 1 or rol_id in roles_permitidos:
                return f(*args, **kwargs)

            flash("Acceso Denegado: Tu cuenta no tiene permisos suficientes para ingresar a esta sección.", "warning")
            return redirect(url_for('index'))
        return decorated_function
    return decorator
