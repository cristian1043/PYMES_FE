from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.services.auth_service import AuthService
from src.services.empresas_service import EmpresasService

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
            # Obtener el rol real del usuario desde la base de datos
            real_rol_id = int(usuario.get('id_rol', 2))
            estado_usuario = usuario.get('estado', 'Activo')

            if estado_usuario == 'Desvinculado':
                flash("Acceso Denegado: Tu cuenta ha sido desvinculada por el Administrador.", "danger")
                return redirect(url_for('auth.login'))

            session['usuario'] = {
                'id': usuario.get('id'),
                'nombre': f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip(),
                'email': usuario.get('email'),
                'rol_id': real_rol_id,
                'estado': estado_usuario
            }
            
            # Obtener las empresas reales almacenadas en la base de datos MySQL
            empresas_db = EmpresasService.obtener_todas()
            session['empresas'] = empresas_db
            
            flash(f"¡Bienvenido/a {session['usuario']['nombre']}!", "success")
            return redirect(url_for('auth.seleccionar_empresa'))

    return render_template('login.html')

@auth_bp.route('/seleccionar_empresa', methods=['GET'])
def seleccionar_empresa():
    """Pantalla con tarjetas para elegir en qué empresa trabajar."""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))

    # Consultar empresas reales en el Backend
    empresas = EmpresasService.obtener_todas()
    session['empresas'] = empresas
    return render_template('seleccionar_empresa.html', empresas=empresas)

@auth_bp.route('/seleccionar_empresa/<int:empresa_id>', methods=['GET'])
def activar_empresa(empresa_id):
    """Establece la empresa activa en la sesión respetando el rol del usuario."""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))

    empresas = EmpresasService.obtener_todas()
    empresa_seleccionada = next((e for e in empresas if e['id'] == empresa_id), None)

    if not empresa_seleccionada:
        flash("La empresa seleccionada no existe.", "danger")
        return redirect(url_for('auth.seleccionar_empresa'))

    # Mantener el rol real del usuario logueado en la sesión
    session['empresa_activa'] = empresa_seleccionada
    # Asignar rol_nombre legible para la interfaz
    rol_id = session['usuario']['rol_id']
    roles_nombres = {1: 'Administrador', 2: 'Vendedor', 3: 'Almacenista'}
    session['empresa_activa']['rol_nombre'] = roles_nombres.get(rol_id, 'Vendedor')
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
            'username': request.form.get('username') or request.form.get('email').split('@')[0],
            'password_hash': request.form.get('password'),
            'id_rol': int(request.form.get('id_rol', 2)),
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
