from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

# Lista de empresas predeterminadas/asociadas de demostración
EMPRESAS_DISPONIBLES = [
    {
        'id': 1,
        'nombre': 'Empresa Chaneques S.A.S.',
        'nit': '900.123.456-1',
        'rol_id': 1,
        'rol_nombre': 'Administrador',
        'icono': '🏢',
        'color': '#1e3c72'
    },
    {
        'id': 2,
        'nombre': 'Empresa La Vainilla S.A.S.',
        'nit': '900.654.321-2',
        'rol_id': 2,
        'rol_nombre': 'Vendedor',
        'icono': '🏬',
        'color': '#2a5298'
    }
]

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Formulario e inicio de sesión de usuario."""
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
                'rol_id': usuario.get('id_rol', 1)
            }
            # Guardar empresas asignadas en sesión
            session['empresas'] = EMPRESAS_DISPONIBLES
            flash(f"¡Bienvenido/a {session['usuario']['nombre']}!", "success")
            
            # Redirigir al selector de empresas
            return redirect(url_for('auth.seleccionar_empresa'))

    return render_template('login.html')

@auth_bp.route('/seleccionar_empresa', methods=['GET'])
def seleccionar_empresa():
    """Pantalla con tarjetas para elegir en qué empresa trabajar."""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))

    empresas = session.get('empresas', EMPRESAS_DISPONIBLES)
    return render_template('seleccionar_empresa.html', empresas=empresas)

@auth_bp.route('/seleccionar_empresa/<int:empresa_id>', methods=['GET'])
def activar_empresa(empresa_id):
    """Establece la empresa activa en la sesión y redirige al dashboard."""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))

    empresas = session.get('empresas', EMPRESAS_DISPONIBLES)
    empresa_seleccionada = next((e for e in empresas if e['id'] == empresa_id), None)

    if not empresa_seleccionada:
        flash("La empresa seleccionada no existe o no tienes acceso.", "danger")
        return redirect(url_for('auth.seleccionar_empresa'))

    # Establecer la empresa activa y su rol específico
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
            'id_rol': int(request.form.get('id_rol', 1))
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
