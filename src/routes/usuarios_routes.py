from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.services.usuarios_service import UsuariosService
from src.services.auth_service import AuthService
from src.utils.decorators import requiere_rol

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@usuarios_bp.route('/', methods=['GET'])
@requiere_rol(1) # Exclusivo para Administrador
def ver_usuarios():
    """Muestra la tabla de gestión de usuarios calculando el estado exclusivo para la empresa activa."""
    empresa_activa = session.get('empresa_activa', {})
    empresa_id = empresa_activa.get('id', 1)

    usuarios = UsuariosService.obtener_todos()
    roles = UsuariosService.obtener_roles()

    # Asignar el estado independiente específico de esta empresa para cada usuario
    for u in usuarios:
        u['estado'] = UsuariosService.obtener_estado_en_empresa(u['id'], empresa_id)

    return render_template('usuarios/ver_usuarios.html', usuarios=usuarios, roles=roles)

@usuarios_bp.route('/afiliar', methods=['POST'])
@requiere_rol(1) # Exclusivo para Administrador
def afiliar_usuario():
    """Afilia a un trabajador asegurando estado Activo exclusivo en la empresa activa."""
    empresa_activa = session.get('empresa_activa', {})
    empresa_id = empresa_activa.get('id', 1)

    email = request.form.get('email')
    documento = request.form.get('documento')
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    telefono = request.form.get('telefono', '')
    id_rol = int(request.form.get('id_rol', 2))
    password = request.form.get('password', '123456')
    tipo_doc = request.form.get('tipo_documento', 'CC')

    banco = request.form.get('banco', '')
    tipo_cuenta = request.form.get('tipo_cuenta', '')
    numero_cuenta = request.form.get('numero_cuenta', '')

    datos = {
        'tipo_documento': tipo_doc,
        'documento': documento,
        'nombre': nombre,
        'apellido': apellido,
        'telefono': telefono,
        'email': email,
        'username': email.split('@')[0],
        'password_hash': password,
        'id_rol': id_rol,
        'estado': 'Activo',
        'banco': banco,
        'tipo_cuenta': tipo_cuenta,
        'numero_cuenta': numero_cuenta
    }

    res, err = AuthService.registrar(datos)
    
    # Marcar estado Activo específicamente en esta empresa
    if res and 'id' in res:
        UsuariosService.cambiar_estado_en_empresa(res['id'], empresa_id, 'Activo')

    if err:
        flash(f"Información: {err}. Se ha vinculado al empleado a esta empresa.", "info")
    else:
        flash(f"¡Trabajador {nombre} {apellido} afiliado exitosamente a esta empresa!", "success")

    return redirect(url_for('usuarios.ver_usuarios'))

@usuarios_bp.route('/cambiar_rol/<int:id>', methods=['POST'])
@requiere_rol(1)
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
@requiere_rol(1)
def cambiar_estado(id):
    """Persiste la desvinculación o reactivación exclusivamente para la empresa activa."""
    empresa_activa = session.get('empresa_activa', {})
    empresa_id = empresa_activa.get('id', 1)

    estado_actual = request.form.get('estado', 'Activo')
    nuevo_estado = 'Desvinculado' if estado_actual == 'Activo' else 'Activo'

    UsuariosService.cambiar_estado_en_empresa(id, empresa_id, nuevo_estado)
    flash(f"El trabajador ha sido actualizado a estado {nuevo_estado} exclusivamente en esta empresa.", "info")

    return redirect(url_for('usuarios.ver_usuarios'))
