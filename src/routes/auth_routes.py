import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.services.auth_service import AuthService
from src.services.empresas_service import EmpresasService
from src.services.usuarios_service import UsuariosService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Formulario e inicio de sesión global de usuario."""
    if 'usuario' in session and 'empresa_activa' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        identificador = request.form.get('identificador')
        password = request.form.get('password')

        usuario, error = AuthService.autenticar(identificador, password)

        if error:
            flash(error, "danger")
        else:
            real_rol_id = int(usuario.get('id_rol', 2))
            usuario_id = usuario.get('id')

            session['usuario'] = {
                'id': usuario_id,
                'nombre': f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip() if usuario.get('apellido') and usuario.get('apellido') not in str(usuario.get('nombre', '')) else usuario.get('nombre', ''),
                'email': usuario.get('email'),
                'username': usuario.get('username'),
                'documento': usuario.get('documento'),
                'tipo_documento': usuario.get('tipo_documento', 'CC'),
                'telefono': usuario.get('telefono', ''),
                'rol_id': real_rol_id,
                'rol_id_global': real_rol_id
            }
            
            # Cargar y filtrar empresas según el estado del rol y estado operativo de la empresa
            empresas_db = EmpresasService.obtener_todas()
            if real_rol_id == 1:
                empresas_activas = empresas_db
            else:
                empresas_activas = [
                    emp for emp in empresas_db 
                    if emp.get('estado', 'Activo') == 'Activo' and 
                    UsuariosService.obtener_vinculacion_empresa(usuario_id, emp['id']).get('estado', 'No Vinculado') == 'Activo'
                ]

            session['empresas'] = empresas_activas
            
            flash(f"¡Bienvenido/a {session['usuario']['nombre']}!", "success")
            return redirect(url_for('auth.seleccionar_empresa'))

    return render_template('login.html')

@auth_bp.route('/seleccionar_empresa', methods=['GET'])
def seleccionar_empresa():
    """Pantalla con tarjetas de empresas calculando el rol exclusivo de cada empresa para el usuario."""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))

    usuario_actual = session['usuario']
    usuario_id = usuario_actual['id']
    rol_id_global = usuario_actual.get('rol_id_global') or usuario_actual.get('rol_id', 2)

    empresas_todas = EmpresasService.obtener_todas()

    empresas_visibles = []
    for emp in empresas_todas:
        if isinstance(emp, dict):
            vinculacion = UsuariosService.obtener_vinculacion_empresa(usuario_id, emp['id'])
            estado_vinc = vinculacion.get('estado', 'No Vinculado')
            rol_vinc = 1 if int(rol_id_global) == 1 else vinculacion.get('rol_id', rol_id_global)

            # El Admin Global (rol_id 1) ve todas las empresas. Los demás ven solo en las que están 'Activo'
            if rol_id_global == 1 or estado_vinc == 'Activo':
                emp_copy = dict(emp)
                emp_copy['rol_id'] = rol_vinc
                roles_nombres = {1: 'Administrador', 2: 'Vendedor', 3: 'Almacenista'}
                emp_copy['rol_nombre'] = roles_nombres.get(rol_vinc, 'Vendedor')
                empresas_visibles.append(emp_copy)

    session['empresas'] = empresas_visibles
    return render_template('seleccionar_empresa.html', empresas=empresas_visibles)

@auth_bp.route('/seleccionar_empresa/<int:empresa_id>', methods=['GET'])
def activar_empresa(empresa_id):
    """Establece la empresa activa bloqueando el acceso a empleados en empresas inactivas."""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))

    usuario_actual = session['usuario']
    usuario_id = usuario_actual['id']
    rol_id_global = usuario_actual.get('rol_id_global') or usuario_actual.get('rol_id', 2)

    empresas = EmpresasService.obtener_todas()
    empresa_seleccionada = next((e for e in empresas if e['id'] == empresa_id), None)

    if not empresa_seleccionada:
        flash("La empresa seleccionada no existe.", "danger")
        return redirect(url_for('auth.seleccionar_empresa'))

    # Bloqueo para trabajadores si la empresa está operativamente INACTIVA
    if int(rol_id_global) != 1 and empresa_seleccionada.get('estado') == 'Inactivo':
        flash("Acceso Denegado: Las operaciones de esta empresa han sido pausadas por el Administrador.", "danger")
        return redirect(url_for('auth.seleccionar_empresa'))

    # Bloqueo si el trabajador no tiene vinculación Activa en la empresa (No Vinculado / Desvinculado / Inactivo)
    vinculacion = UsuariosService.obtener_vinculacion_empresa(usuario_id, empresa_id)
    if int(rol_id_global) != 1 and vinculacion.get('estado') != 'Activo':
        flash("Acceso Denegado: No tienes una vinculación activa y autorizada en esta empresa.", "danger")
        return redirect(url_for('auth.seleccionar_empresa'))

    # Asignar rol exclusivo de esta empresa para el usuario (Admin Global conserva rol 1)
    rol_especifico = 1 if int(rol_id_global) == 1 else vinculacion.get('rol_id', rol_id_global)
    session['usuario']['rol_id'] = rol_especifico
    session['usuario']['rol_id_global'] = rol_id_global

    session['empresa_activa'] = empresa_seleccionada
    roles_nombres = {1: 'Administrador', 2: 'Vendedor', 3: 'Almacenista'}
    session['empresa_activa']['rol_nombre'] = roles_nombres.get(rol_especifico, 'Vendedor')
    session['empresa_activa']['icono'] = '🏢'

    flash(f"Entraste a trabajar en {empresa_seleccionada['nombre']}", "info")
    return redirect(url_for('index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Formulario y registro de un nuevo usuario en la plataforma."""
    if 'usuario' in session and 'empresa_activa' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        datos = {
            'tipo_documento': request.form.get('tipo_documento'),
            'documento': request.form.get('documento'),
            'nombre': request.form.get('nombre'),
            'apellido': request.form.get('apellido'),
            'telefono': request.form.get('telefono'),
            'email': request.form.get('email'),
            'username': request.form.get('username') or '',
            'password_hash': request.form.get('password'),
            'id_rol': int(request.form.get('id_rol', 2)),
            'estado': 'Activo',
            'fecha_nacimiento': request.form.get('fecha_nacimiento') or '',
            'lugar_residencia': request.form.get('lugar_residencia') or '',
            'estado_civil': request.form.get('estado_civil') or '',
            'numero_hijos': request.form.get('numero_hijos') or 0,
            'banco': request.form.get('banco') or '',
            'tipo_cuenta': request.form.get('tipo_cuenta') or '',
            'numero_cuenta': request.form.get('numero_cuenta') or ''
        }

        res, err = AuthService.registrar(datos)
        if err:
            flash(f"Error al registrar la cuenta: {err}", "danger")
        else:
            uname = res.get('username') if isinstance(res, dict) and res.get('username') else ''
            msg_usuario = f" Tu identificador asignado es @{uname}." if uname else ""
            flash(f"¡Cuenta creada exitosamente!{msg_usuario} Ya puedes iniciar sesión con tu correo o @{uname}.", "success")
            return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """Cierra la sesión del usuario actual."""
    session.clear()
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for('auth.login'))

@auth_bp.route('/recuperar_password', methods=['GET', 'POST'])
def recuperar_password():
    """Flujo de solicitud de recuperación de contraseña vía correo o código OTP."""
    token = request.args.get('token')
    if token:
        return render_template('recuperar_password.html', token=token, paso_codigo=True)

    if request.method == 'POST':
        identificador = request.form.get('identificador', '').strip()
        if not identificador:
            flash("Por favor ingresa tu correo, usuario o documento.", "warning")
            return render_template('recuperar_password.html')

        res, err = AuthService.solicitar_recuperacion(identificador)
        if err:
            flash(f"No se pudo generar la solicitud: {err}", "danger")
            return render_template('recuperar_password.html')

        token_generado = res.get('token') if isinstance(res, dict) else ''
        codigo_generado = res.get('codigo') if isinstance(res, dict) else ''
        email_enmascarado = res.get('email_enmascarado', '') if isinstance(res, dict) else ''
        enviado_smtp = bool(res.get('enviado_smtp')) if isinstance(res, dict) else False
        link_directo = res.get('link_directo', '') if isinstance(res, dict) else ''

        if enviado_smtp:
            flash(f"Hemos enviado el código de verificación de 6 dígitos a tu correo {email_enmascarado}.", "success")
        else:
            flash(f"Solicitud verificada para {email_enmascarado}. Tu código de verificación de 6 dígitos ha sido generado.", "success")

        return render_template(
            'recuperar_password.html',
            token='',
            codigo=codigo_generado,
            email_enmascarado=email_enmascarado,
            enviado_smtp=enviado_smtp,
            token_respaldo=token_generado,
            paso_codigo=True,
            link_directo=link_directo
        )

    return render_template('recuperar_password.html')

@auth_bp.route('/recuperar_password_confirmar', methods=['POST'])
def recuperar_password_confirmar():
    """Aplica la nueva contraseña utilizando el token temporal o código OTP recibido."""
    token_o_codigo = request.form.get('token_o_codigo', '').strip()
    password_nueva = request.form.get('password_nueva', '').strip()
    password_confirmar = request.form.get('password_confirmar', '').strip()
    codigo_previo = request.form.get('codigo_previo', '').strip()

    if not token_o_codigo:
        flash("El código de verificación de 6 dígitos es obligatorio.", "danger")
        return render_template('recuperar_password.html', codigo=codigo_previo, paso_codigo=True)

    if not password_nueva or len(password_nueva) < 6:
        flash("La nueva contraseña debe tener al menos 6 caracteres.", "warning")
        return render_template('recuperar_password.html', token=token_o_codigo, codigo=codigo_previo, paso_codigo=True)

    if password_nueva != password_confirmar:
        flash("Las contraseñas no coinciden. Por favor verifica.", "danger")
        return render_template('recuperar_password.html', token=token_o_codigo, codigo=codigo_previo, paso_codigo=True)

    res, err = AuthService.confirmar_recuperacion(token_o_codigo, password_nueva)
    if err:
        flash(f"Error al restablecer contraseña: {err}", "danger")
        return render_template('recuperar_password.html', token=token_o_codigo, codigo=codigo_previo, paso_codigo=True)

    flash("¡Tu contraseña ha sido restablecida con éxito! Ya puedes iniciar sesión.", "success")
    return redirect(url_for('auth.login'))
