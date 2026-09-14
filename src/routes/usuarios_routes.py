from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from src.services.usuarios_service import UsuariosService
from src.services.auth_service import AuthService
from src.utils.decorators import requiere_rol

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@usuarios_bp.route('/', methods=['GET'])
@requiere_rol(1) # Exclusivo para Administrador
def ver_usuarios():
    """Muestra la tabla de gestión de personal con buscador interactivo y filtros."""
    empresa_activa = session.get('empresa_activa', {})
    empresa_id = empresa_activa.get('id', 1)

    q = request.args.get('q', '').strip()
    filtro = request.args.get('filtro', '').strip()

    usuarios_res = UsuariosService.obtener_todos(q=q, filtro=filtro)
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

    return render_template('usuarios/ver_usuarios.html', usuarios=usuarios, roles=roles, q=q, filtro=filtro)

@usuarios_bp.route('/buscar_candidato', methods=['GET'])
@requiere_rol(1)
def buscar_candidato():
    """Busca y extrae en tiempo real los datos personales y bancarios de un usuario mediante su @username, documento o ID."""
    identificador = request.args.get('identificador', '').strip()
    if not identificador:
        return jsonify({"encontrado": False, "mensaje": "Ingresa un identificador válido (@username, documento o ID)."}), 400

    # 1. Intentar por username
    candidato = UsuariosService.obtener_por_username(identificador)
    # 2. Si no, por documento
    if not candidato:
        candidato = UsuariosService.obtener_por_documento(identificador)
    # 3. Si es numérico y aún no se encuentra, intentar por ID
    if not candidato and identificador.isdigit():
        candidato = UsuariosService.obtener_por_id(int(identificador))

    if candidato and isinstance(candidato, dict) and 'id' in candidato:
        empresa_activa = session.get('empresa_activa', {})
        empresa_id = empresa_activa.get('id', 1)
        vinc = UsuariosService.obtener_vinculacion_empresa(candidato['id'], empresa_id)
        ya_vinculado = vinc.get('estado') == 'Activo'

        return jsonify({
            "encontrado": True,
            "usuario": candidato,
            "ya_vinculado": ya_vinculado,
            "rol_actual": vinc.get('rol_id', 2)
        }), 200

    return jsonify({
        "encontrado": False,
        "mensaje": f"No se encontró ningún usuario con el identificador '{identificador}'. Verifica que la persona haya creado previamente su cuenta."
    }), 404

@usuarios_bp.route('/afiliar', methods=['POST'])
@requiere_rol(1) # Exclusivo para Administrador
def afiliar_usuario():
    """Afilia a un trabajador tras revisar sus datos personales en la tarjeta de previsualización."""
    empresa_activa = session.get('empresa_activa', {})
    empresa_id = empresa_activa.get('id', 1)

    usuario_id = request.form.get('usuario_id', '').strip()
    identificador = request.form.get('identificador', '').strip()
    id_rol = int(request.form.get('id_rol', 2))
    banco = request.form.get('banco', '').strip()
    tipo_cuenta = request.form.get('tipo_cuenta', '').strip()
    numero_cuenta = request.form.get('numero_cuenta', '').strip()

    usuario_existente = None
    if usuario_id and usuario_id.isdigit():
        usuario_existente = UsuariosService.obtener_por_id(int(usuario_id))
    elif identificador:
        usuario_existente = UsuariosService.obtener_por_username(identificador) or UsuariosService.obtener_por_documento(identificador)

    if not usuario_existente or 'id' not in usuario_existente:
        flash(f"No fue posible vincular al trabajador: Usuario no encontrado.", "danger")
        return redirect(url_for('usuarios.ver_usuarios'))

    u_id = usuario_existente['id']
    u_nombre = f"{usuario_existente.get('nombre', '')} {usuario_existente.get('apellido', '')}".strip()
    u_username = usuario_existente.get('username') or ''

    # Actualizar datos bancarios si se modificaron o completaron en el formulario
    if banco or numero_cuenta:
        datos_bancarios = {
            'banco': banco or usuario_existente.get('banco', ''),
            'tipo_cuenta': tipo_cuenta or usuario_existente.get('tipo_cuenta', 'Ahorros'),
            'numero_cuenta': numero_cuenta or usuario_existente.get('numero_cuenta', '')
        }
        UsuariosService.actualizar(u_id, datos_bancarios)

    # Afiliar y activar en la empresa activa con el rol seleccionado
    UsuariosService.cambiar_rol_en_empresa(u_id, empresa_id, id_rol)
    UsuariosService.cambiar_estado_en_empresa(u_id, empresa_id, 'Activo')

    flash(f"¡Trabajador {u_nombre} (@{u_username}) aprobado y vinculado exitosamente a esta empresa!", "success")
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
            'nombre': request.form.get('nombre'),
            'apellido': request.form.get('apellido'),
            'email': request.form.get('email'),
            'telefono': request.form.get('telefono'),
            'banco': request.form.get('banco', ''),
            'tipo_cuenta': request.form.get('tipo_cuenta', ''),
            'numero_cuenta': request.form.get('numero_cuenta', ''),
            'fecha_nacimiento': request.form.get('fecha_nacimiento', ''),
            'lugar_residencia': request.form.get('lugar_residencia', ''),
            'estado_civil': request.form.get('estado_civil', ''),
            'numero_hijos': request.form.get('numero_hijos', 0)
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

@usuarios_bp.route('/perfil', methods=['GET', 'POST'])
def perfil():
    """Muestra y permite actualizar la información personal y contraseña del usuario activo."""
    usuario_sesion = session.get('usuario')
    if not usuario_sesion or not usuario_sesion.get('id'):
        flash("Debes iniciar sesión para acceder a tu perfil.", "warning")
        return redirect(url_for('auth.login'))

    user_id = usuario_sesion.get('id')
    empresa_activa = session.get('empresa_activa')
    empresa_id = empresa_activa.get('id') if empresa_activa else None

    if request.method == 'POST':
        # 1. Gestión de Contraseña con validación de clave actual
        password_actual = request.form.get('password_actual', '').strip()
        password_nueva = request.form.get('password_nueva', '').strip()
        password_confirmar = request.form.get('password_confirmar', '').strip()

        if password_actual or password_nueva:
            if not password_actual:
                flash("Debes ingresar tu contraseña actual para autorizar el cambio.", "danger")
                return redirect(url_for('usuarios.perfil'))
            if not password_nueva:
                flash("Debes ingresar la nueva contraseña deseada.", "danger")
                return redirect(url_for('usuarios.perfil'))
            if len(password_nueva) < 6:
                flash("La nueva contraseña debe tener al menos 6 caracteres.", "warning")
                return redirect(url_for('usuarios.perfil'))
            if password_nueva != password_confirmar:
                flash("La confirmación de la nueva contraseña no coincide.", "danger")
                return redirect(url_for('usuarios.perfil'))

            res_pass, err_pass = AuthService.cambiar_password(user_id, password_actual, password_nueva)
            if err_pass:
                flash(f"No se pudo cambiar la contraseña: {err_pass}", "danger")
                return redirect(url_for('usuarios.perfil'))
            else:
                flash("¡Contraseña actualizada exitosamente con validación de seguridad!", "success")

        # 2. Actualización de Datos Personales y Bancarios
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        email = request.form.get('email', '').strip()
        telefono = request.form.get('telefono', '').strip()
        banco = request.form.get('banco', '').strip()
        tipo_cuenta = request.form.get('tipo_cuenta', '').strip()
        numero_cuenta = request.form.get('numero_cuenta', '').strip()
        fecha_nacimiento = request.form.get('fecha_nacimiento', '').strip()
        lugar_residencia = request.form.get('lugar_residencia', '').strip()
        estado_civil = request.form.get('estado_civil', '').strip()
        numero_hijos = request.form.get('numero_hijos', 0)

        datos_actualizar = {
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "telefono": telefono,
            "banco": banco,
            "tipo_cuenta": tipo_cuenta,
            "numero_cuenta": numero_cuenta,
            "fecha_nacimiento": fecha_nacimiento,
            "lugar_residencia": lugar_residencia,
            "estado_civil": estado_civil,
            "numero_hijos": numero_hijos
        }

        res_u, err_u = UsuariosService.actualizar(user_id, datos_actualizar)
        if err_u:
            flash(f"Error al actualizar la información personal: {err_u}", "danger")
        else:
            flash("¡Información personal actualizada correctamente!", "success")
            usuario_sesion['nombre'] = f"{nombre} {apellido}".strip()
            usuario_sesion['email'] = email
            session['usuario'] = usuario_sesion

        return redirect(url_for('usuarios.perfil'))

    usuario = UsuariosService.obtener_por_id(user_id) or usuario_sesion
    rol_nombre = None
    if empresa_id:
        vinculacion = UsuariosService.obtener_vinculacion_empresa(user_id, empresa_id)
        rol_nombre = vinculacion.get('rol_nombre') if (vinculacion and isinstance(vinculacion, dict)) else session.get('usuario', {}).get('rol_nombre', 'Vendedor')

    return render_template('usuarios/perfil.html', usuario=usuario, rol_nombre=rol_nombre, empresa_activa=empresa_activa)

