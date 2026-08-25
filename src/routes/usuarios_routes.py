from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.services.usuarios_service import UsuariosService
from src.services.auth_service import AuthService
from src.utils.decorators import requiere_rol

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@usuarios_bp.route('/', methods=['GET'])
@requiere_rol(1) # Exclusivo para Administrador
def ver_usuarios():
    """Muestra la tabla de gestión de usuarios calculando rol y estado exclusivos para la empresa activa."""
    empresa_activa = session.get('empresa_activa', {})
    empresa_id = empresa_activa.get('id', 1)

    usuarios_res = UsuariosService.obtener_todos()
    roles = UsuariosService.obtener_roles()

    usuarios = usuarios_res.get("items", []) if isinstance(usuarios_res, dict) else (usuarios_res if isinstance(usuarios_res, list) else [])

    # Asignar rol y estado independientes para esta empresa a cada usuario
    for u in usuarios:
        if isinstance(u, dict):
            u_id = u.get('id')
            vinculacion = UsuariosService.obtener_vinculacion_empresa(u_id, empresa_id) if u_id else {}
            if isinstance(vinculacion, dict):
                u['id_rol'] = int(vinculacion.get('rol_id', u.get('id_rol', 2)))
                u['estado'] = str(vinculacion.get('estado', 'Activo'))
            else:
                u['id_rol'] = int(u.get('id_rol', 2))
                u['estado'] = 'Activo'

    return render_template('usuarios/ver_usuarios.html', usuarios=usuarios, roles=roles)

@usuarios_bp.route('/afiliar', methods=['POST'])
@requiere_rol(1) # Exclusivo para Administrador
def afiliar_usuario():
    """Afilia a un trabajador existente verificando que su cuenta ya esté registrada previamente en el sistema."""
    empresa_activa = session.get('empresa_activa', {})
    empresa_id = empresa_activa.get('id', 1)

    documento = request.form.get('documento', '').strip()
    id_rol = int(request.form.get('id_rol', 2))
    banco = request.form.get('banco', '').strip()
    tipo_cuenta = request.form.get('tipo_cuenta', '').strip()
    numero_cuenta = request.form.get('numero_cuenta', '').strip()

    if not documento:
        flash("Debes ingresar un número de documento válido para buscar al trabajador.", "warning")
        return redirect(url_for('usuarios.ver_usuarios'))

    # Buscar si la persona ya existe en la base de datos global de usuarios
    usuario_existente = UsuariosService.obtener_por_documento(documento)

    if not usuario_existente or 'id' not in usuario_existente:
        flash(f"El número de documento N° {documento} no corresponde a ninguna cuenta registrada en el sistema. El trabajador debe crear su cuenta previamente.", "danger")
        return redirect(url_for('usuarios.ver_usuarios'))

    u_id = usuario_existente['id']
    u_nombre = f"{usuario_existente.get('nombre', '')} {usuario_existente.get('apellido', '')}".strip()

    # Actualizar datos bancarios del perfil si fueron diligenciados
    if banco or numero_cuenta:
        datos_bancarios = {
            'banco': banco or usuario_existente.get('banco', ''),
            'tipo_cuenta': tipo_cuenta or usuario_existente.get('tipo_cuenta', 'Ahorros'),
            'numero_cuenta': numero_cuenta or usuario_existente.get('numero_cuenta', '')
        }
        UsuariosService.actualizar(u_id, datos_bancarios)

    # Afiliar y activar exclusivamente en la empresa activa con el rol seleccionado
    UsuariosService.cambiar_rol_en_empresa(u_id, empresa_id, id_rol)
    UsuariosService.cambiar_estado_en_empresa(u_id, empresa_id, 'Activo')

    flash(f"¡Trabajador {u_nombre} (Doc: {documento}) afiliado exitosamente a esta empresa!", "success")
    return redirect(url_for('usuarios.ver_usuarios'))

@usuarios_bp.route('/cambiar_rol/<int:id>', methods=['POST'])
@requiere_rol(1)
def cambiar_rol(id):
    """Procesa el cambio de rol exclusivamente para la empresa activa."""
    empresa_activa = session.get('empresa_activa', {})
    empresa_id = empresa_activa.get('id', 1)

    nuevo_rol_id = request.form.get('id_rol')
    if not nuevo_rol_id:
        flash("Debes seleccionar un rol válido.", "danger")
        return redirect(url_for('usuarios.ver_usuarios'))

    UsuariosService.cambiar_rol_en_empresa(id, empresa_id, nuevo_rol_id)
    flash("Rol de usuario actualizado exitosamente para esta empresa.", "success")

    return redirect(url_for('usuarios.ver_usuarios'))

@usuarios_bp.route('/cambiar_estado/<int:id>', methods=['POST'])
@requiere_rol(1)
def cambiar_estado(id):
    """Persiste la desvinculación o reactivación exclusivamente para la empresa activa."""
    empresa_activa = session.get('empresa_activa', {})
    empresa_id = empresa_activa.get('id', 1)

    estado_actual = request.form.get('estado', 'Activo')
    nuevo_estado = 'Desvinculado' if estado_actual == 'Activo' else 'Activo'

    res, err = UsuariosService.cambiar_estado_en_empresa(id, empresa_id, nuevo_estado)
    if err:
        flash(f"Error al cambiar el estado del trabajador: {err}", "danger")
    else:
        flash(f"El trabajador ha sido actualizado a estado {nuevo_estado} exclusivamente en esta empresa.", "info")
    return redirect(url_for('usuarios.ver_usuarios'))

@usuarios_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@requiere_rol(1) # Exclusivo para Administrador
def editar_usuario(id):
    """Formulario y procesamiento para que el Administrador edite los datos de un usuario."""
    usuario = UsuariosService.obtener_por_id(id)
    if not usuario:
        flash("El usuario especificado no existe", "warning")
        return redirect(url_for('usuarios.ver_usuarios'))

    empresa_activa = session.get('empresa_activa', {})
    empresa_id = empresa_activa.get('id', 1)

    if request.method == 'POST':
        id_rol = int(request.form.get('id_rol', usuario.get('id_rol', 2)))
        datos = {
            'tipo_documento': request.form.get('tipo_documento'),
            'documento': request.form.get('documento'),
            'nombre': request.form.get('nombre'),
            'apellido': request.form.get('apellido'),
            'email': request.form.get('email'),
            'telefono': request.form.get('telefono'),
            'banco': request.form.get('banco', ''),
            'tipo_cuenta': request.form.get('tipo_cuenta', ''),
            'numero_cuenta': request.form.get('numero_cuenta', '')
        }

        # Actualizar datos de perfil de usuario
        res, err = UsuariosService.actualizar(id, datos)
        # Actualizar rol exclusivo en la empresa activa
        UsuariosService.cambiar_rol_en_empresa(id, empresa_id, id_rol)

        if err:
            flash(f"Error al actualizar el usuario: {err}", "danger")
        else:
            flash(f"Usuario {datos['nombre']} {datos['apellido']} actualizado exitosamente", "success")
            return redirect(url_for('usuarios.ver_usuarios'))

    roles = UsuariosService.obtener_roles()
    vinculacion = UsuariosService.obtener_vinculacion_empresa(id, empresa_id)
    usuario['id_rol'] = vinculacion.get('rol_id', usuario.get('id_rol', 2))
    return render_template('usuarios/editar_usuario.html', usuario=usuario, roles=roles)
