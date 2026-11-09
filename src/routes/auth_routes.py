from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.services.auth_service import AuthService
from src.services.empresas_service import EmpresasService
from src.services.usuarios_service import UsuariosService

auth_bp = Blueprint('auth', __name__)

ICONOS_EMPRESA = ['🏢', '🏪', '🏭', '🏬', '🛠️', '💼']
ROLES_NOMBRES = {1: 'Administrador', 2: 'Vendedor', 3: 'Almacenista'}


def _enriquecer_empresas_usuario(usuario):
    """
    Obtiene las empresas autorizadas para el usuario y adjunta el rol específico
    que el usuario desempeña en cada empresa.
    """
    user_id = usuario.get('id') if isinstance(usuario, dict) else None
    es_super_admin = bool(usuario.get('es_super_admin', False)) if isinstance(usuario, dict) else False
    empresas_raw = EmpresasService.obtener_todas(filtrar_por_usuario=True)

    empresas_enriquecidas = []
    for idx, emp in enumerate(empresas_raw):
        if not isinstance(emp, dict):
            continue
        emp_copy = dict(emp)
        emp_id = emp_copy.get('id')
        emp_copy.setdefault('icono', ICONOS_EMPRESA[idx % len(ICONOS_EMPRESA)])

        if es_super_admin:
            rol_id = 1
            rol_nombre = 'Super Admin'
        else:
            vinc = UsuariosService.obtener_vinculacion_empresa(user_id, emp_id) if (user_id and emp_id) else {}
            if isinstance(vinc, dict) and vinc.get('estado') == 'Desvinculado':
                continue
            rol_id = int(vinc.get('rol_id') or usuario.get('rol_id') or usuario.get('id_rol') or 2)
            rol_nombre = vinc.get('rol_nombre') or ROLES_NOMBRES.get(rol_id, 'Vendedor')

        emp_copy['rol_id'] = rol_id
        emp_copy['rol_nombre'] = rol_nombre
        empresas_enriquecidas.append(emp_copy)

    session['empresas'] = empresas_enriquecidas
    return empresas_enriquecidas


def _activar_empresa_en_sesion(emp):
    """Configura `empresa_activa` y actualiza el `rol_id` contextual del usuario para esa empresa."""
    session['empresa_activa'] = emp
    session['empresa_id'] = emp.get('id')
    if 'usuario' in session and isinstance(session['usuario'], dict):
        rol_emp = int(emp.get('rol_id', 2))
        session['usuario']['rol_id'] = rol_emp
        session['usuario']['id_rol'] = rol_emp
        session['usuario']['rol_nombre'] = emp.get('rol_nombre', ROLES_NOMBRES.get(rol_emp, 'Vendedor'))
    session.modified = True


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identificador = (request.form.get('email') or request.form.get('identificador') or '').strip()
        password = request.form.get('password') or ''

        usuario, error = AuthService.autenticar(identificador, password)
        if error or not usuario:
            flash(error or "Credenciales inválidas. Intenta nuevamente.", "danger")
            return render_template('login.html')

        empresas = _enriquecer_empresas_usuario(usuario)
        if len(empresas) == 1:
            emp = empresas[0]
            if emp.get('estado') == 'Inactivo' and emp.get('rol_id') != 1:
                flash("Tu empresa asignada se encuentra pausada por el Administrador.", "warning")
                return redirect(url_for('auth.seleccionar_empresa'))
            _activar_empresa_en_sesion(emp)
            flash(f"¡Bienvenido, {usuario.get('nombre')}! Operando en {emp.get('nombre')}.", "success")
            return redirect(url_for('index'))
        elif len(empresas) > 1:
            flash(f"¡Bienvenido, {usuario.get('nombre')}! Selecciona la empresa con la que deseas trabajar.", "info")
            return redirect(url_for('auth.seleccionar_empresa'))
        else:
            flash(f"¡Bienvenido, {usuario.get('nombre')}! Registra una empresa o solicita vinculación a un Administrador.", "info")
            return redirect(url_for('auth.seleccionar_empresa'))

    return render_template('login.html')


@auth_bp.route('/seleccionar_empresa', methods=['GET'])
def seleccionar_empresa():
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))

    empresas = _enriquecer_empresas_usuario(session.get('usuario', {}))
    return render_template('seleccionar_empresa.html', empresas=empresas)


@auth_bp.route('/activar_empresa/<int:empresa_id>', methods=['GET'])
def activar_empresa(empresa_id):
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))

    empresas = _enriquecer_empresas_usuario(session.get('usuario', {}))
    emp = next((e for e in empresas if int(e.get('id', 0)) == int(empresa_id)), None)

    if not emp:
        flash("Acceso denegado: No tienes vinculación activa con la empresa solicitada.", "danger")
        return redirect(url_for('auth.seleccionar_empresa'))

    if emp.get('estado') == 'Inactivo' and int(emp.get('rol_id', 2)) != 1:
        flash("Las operaciones de esta empresa se encuentran pausadas por el Administrador.", "danger")
        return redirect(url_for('auth.seleccionar_empresa'))

    _activar_empresa_en_sesion(emp)

    if emp.get('estado') == 'Inactivo' and int(emp.get('rol_id', 2)) == 1:
        flash(f"Ingresaste a '{emp.get('nombre')}' (Pausada). Puedes reactivarla en Configuración.", "warning")
        return redirect(url_for('empresas.configuracion'))

    flash(f"Espacio de trabajo activo: {emp.get('nombre')} ({emp.get('rol_nombre')})", "success")
    return redirect(url_for('index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        tipo_registro = request.form.get('tipo_registro', 'empleado')
        id_rol_elegido = 1 if tipo_registro == 'dueno' else int(request.form.get('id_rol', 2))

        user_data = {
            "tipo_documento": request.form.get('tipo_documento'),
            "documento": request.form.get('documento'),
            "nombre": request.form.get('nombre'),
            "apellido": request.form.get('apellido'),
            "telefono": request.form.get('telefono'),
            "email": request.form.get('email'),
            "username": request.form.get('username', '').strip().lstrip('@'),
            "password": request.form.get('password'),
            "id_rol": id_rol_elegido,
            "estado": "Activo",
            "fecha_nacimiento": request.form.get('fecha_nacimiento', ''),
            "lugar_residencia": request.form.get('lugar_residencia', ''),
            "estado_civil": request.form.get('estado_civil', ''),
            "numero_hijos": int(request.form.get('numero_hijos') or 0),
            "banco": request.form.get('banco', ''),
            "tipo_cuenta": request.form.get('tipo_cuenta', ''),
            "numero_cuenta": request.form.get('numero_cuenta', '')
        }

        res, err = AuthService.registrar(user_data)
        if err or not res:
            flash(err or "No se pudo completar el registro.", "danger")
            return render_template('register.html')

        username_creado = res.get('username', '') if isinstance(res, dict) else ''

        if tipo_registro == 'dueno':
            usuario_log, err_log = AuthService.autenticar(user_data['email'], user_data['password'])
            if usuario_log and not err_log:
                flash(
                    f"¡Bienvenido, {user_data['nombre']}! Tu cuenta (@{username_creado}) está lista. "
                    f"Ahora registra los datos de tu empresa.",
                    "success"
                )
                return redirect(url_for('empresas.nueva_empresa'))

        flash(
            f"¡Cuenta creada exitosamente! Tu usuario asignado es @{username_creado}. Ahora puedes iniciar sesión.",
            "success"
        )
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/recuperar_password', methods=['GET', 'POST'])
def recuperar_password():
    token = request.args.get('token', '').strip()
    if request.method == 'POST':
        identificador = request.form.get('identificador', '').strip()
        res, err = AuthService.solicitar_recuperacion(identificador)
        if err:
            flash(err, "danger")
        else:
            mensaje = (res.get('mensaje') if isinstance(res, dict) else None) or (
                "Si los datos ingresados coinciden con una cuenta activa, "
                "hemos enviado las instrucciones de recuperación al correo registrado."
            )
            flash(mensaje, "info")
            return render_template(
                'recuperar_password.html',
                token='',
                paso_codigo=True,
                identificador=identificador
            )

    return render_template('recuperar_password.html', token=token, paso_codigo=bool(token))


@auth_bp.route('/recuperar_password/confirmar', methods=['POST'])
def recuperar_password_confirmar():
    token_o_codigo = request.form.get('token_o_codigo', '').strip()
    identificador = request.form.get('identificador', '').strip()
    password_nueva = request.form.get('password_nueva', '')
    password_confirmar = request.form.get('password_confirmar', '')

    if password_nueva != password_confirmar:
        flash('Las contraseñas ingresadas no coinciden.', 'danger')
        return render_template(
            'recuperar_password.html',
            token='',
            paso_codigo=True,
            identificador=identificador
        )

    res, err = AuthService.confirmar_recuperacion(
        token_o_codigo=token_o_codigo,
        password_nueva=password_nueva,
        identificador=identificador
    )
    if err:
        flash(err, 'danger')
        return render_template(
            'recuperar_password.html',
            token='',
            paso_codigo=True,
            identificador=identificador
        )

    mensaje = (res.get('mensaje') if isinstance(res, dict) else None) or "¡Tu contraseña ha sido restablecida exitosamente!"
    flash(mensaje, 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
def logout():
    AuthService.logout()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/logout_global', methods=['POST'])
def logout_global():
    AuthService.logout_global()
    flash('Se ha cerrado tu sesión en todos los dispositivos.', 'warning')
    return redirect(url_for('auth.login'))
