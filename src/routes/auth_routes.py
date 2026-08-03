from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

# Lista de empresas de demostración con estados por usuario
EMPRESAS_DISPONIBLES = [
    {
        'id': 1,
        'nombre': 'Empresa Chaneques S.A.S.',
        'nit': '900.123.456-1',
        'rol_id': 1,
        'rol_nombre': 'Administrador',
        'estado': 'Activo',
        'icono': '🏢',
        'color': '#1e3c72'
    },
    {
        'id': 2,
        'nombre': 'Empresa La Vainilla S.A.S.',
        'nit': '900.654.321-2',
        'rol_id': 2,
        'rol_nombre': 'Vendedor',
        'estado': 'Activo',
        'icono': '🏬',
        'color': '#2a5298'
    }
]

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
            session['usuario'] = {
                'id': usuario.get('id'),
                'nombre': f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip(),
                'email': usuario.get('email'),
                'rol_id': usuario.get('id_rol', 1),
                'estado_global': usuario.get('estado', 'Activo')
            }
            session['empresas'] = EMPRESAS_DISPONIBLES
            flash(f"¡Bienvenido/a {session['usuario']['nombre']}!", "success")
            return redirect(url_for('auth.seleccionar_empresa'))

    return render_template('login.html')

@auth_bp.route('/seleccionar_empresa', methods=['GET'])
def seleccionar_empresa():
    """Pantalla de selección de empresas que muestra únicamente espacios de trabajo activos."""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))

    empresas_todas = session.get('empresas', EMPRESAS_DISPONIBLES)
    
    # Filtrar únicamente las empresas donde la vinculación del usuario esté Activa
    empresas_activas = [e for e in empresas_todas if e.get('estado', 'Activo') == 'Activo']

    return render_template('seleccionar_empresa.html', empresas=empresas_activas)

@auth_bp.route('/seleccionar_empresa/<int:empresa_id>', methods=['GET'])
def activar_empresa(empresa_id):
    """Activa el espacio de trabajo de la empresa seleccionada si está vinculado."""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))

    empresas = session.get('empresas', EMPRESAS_DISPONIBLES)
    empresa_seleccionada = next((e for e in empresas if e['id'] == empresa_id), None)

    if not empresa_seleccionada:
        flash("La empresa seleccionada no existe.", "danger")
        return redirect(url_for('auth.seleccionar_empresa'))

    if empresa_seleccionada.get('estado') == 'Desvinculado':
        flash("Acceso Denegado: Tu cuenta ha sido desvinculada del espacio de trabajo de esta empresa.", "danger")
        return redirect(url_for('auth.seleccionar_empresa'))

    session['empresa_activa'] = empresa_seleccionada
    session['usuario']['rol_id'] = empresa_seleccionada['rol_id']

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
            'username': request.form.get('username') or request.form.get('email').split('@')[0],
            'password_hash': request.form.get('password'),
            'id_rol': int(request.form.get('id_rol', 1)),
            'estado': 'Activo'
        }

        res, err = AuthService.registrar(datos)
        if err:
            flash(f"Error al registrar la cuenta: {err}", "danger")
        else:
            flash("¡Cuenta creada exitosamente! Ya puedes iniciar sesión.", "success")
            return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """Cierra la sesión del usuario actual."""
    session.clear()
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for('auth.login'))
