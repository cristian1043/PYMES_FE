from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.services.usuarios_service import UsuariosService
from src.utils.decorators import requiere_rol

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@usuarios_bp.route('/', methods=['GET'])
@requiere_rol(1) # Exclusivo para Administrador
def ver_usuarios():
    """Muestra la tabla de gestión de usuarios, roles y vinculación (Solo Admin)."""
    usuarios = UsuariosService.obtener_todos()
    roles = UsuariosService.obtener_roles()
    return render_template('usuarios/ver_usuarios.html', usuarios=usuarios, roles=roles)

@usuarios_bp.route('/cambiar_rol/<int:id>', methods=['POST'])
@requiere_rol(1) # Exclusivo para Administrador
def cambiar_rol(id):
    """Procesa el cambio de rol de un usuario en la base de datos."""
    nuevo_rol_id = request.form.get('id_rol')
    if not nuevo_rol_id:
        flash("Debes seleccionar un rol válido.", "danger")
        return redirect(url_for('usuarios.ver_usuarios'))

    res, err = UsuariosService.cambiar_rol(id, nuevo_rol_id)
    if err:
        flash(f"Error al cambiar el rol: {err}", "danger")
    else:
        flash("Rol de usuario actualizado exitosamente.", "success")

    return redirect(url_for('usuarios.ver_usuarios'))

@usuarios_bp.route('/cambiar_estado/<int:id>', methods=['POST'])
@requiere_rol(1) # Exclusivo para Administrador
def cambiar_estado(id):
    """Persiste el cambio de estado (Activo / Desvinculado) en el Backend."""
    estado_actual = request.form.get('estado', 'Activo')
    nuevo_estado = 'Desvinculado' if estado_actual == 'Activo' else 'Activo'

    res, err = UsuariosService.cambiar_estado(id, nuevo_estado)
    if err:
        flash(f"Error al actualizar el estado laboral: {err}", "danger")
    else:
        flash(f"El usuario ha sido actualizado a estado: {nuevo_estado}", "info")

    return redirect(url_for('usuarios.ver_usuarios'))
