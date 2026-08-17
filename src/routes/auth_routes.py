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
                'nombre': f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip(),
                'email': usuario.get('email'),
                'rol_id': real_rol_id
            }
            
            # Cargar y filtrar empresas según el estado del rol y estado operativo de la empresa
            empresas_db = EmpresasService.obtener_todas()
            if real_rol_id == 1:
                empresas_activas = empresas_db
            else:
                empresas_activas = [
                    emp for emp in empresas_db 
                    if emp.get('estado', 'Activo') == 'Activo' and 
                    UsuariosService.obtener_vinculacion_empresa(usuario_id, emp['id']).get('estado', 'Activo') == 'Activo'
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
    rol_id_global = usuario_actual.get('rol_id', 2)

    empresas_todas = EmpresasService.obtener_todas()

    empresas_visibles = []
    for emp in empresas_todas:
        if isinstance(emp, dict):
            vinculacion = UsuariosService.obtener_vinculacion_empresa(usuario_id, emp['id'])
            estado_vinc = vinculacion.get('estado', 'No Vinculado')
            rol_vinc = vinculacion.get('rol_id', rol_id_global)

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
    rol_id_global = usuario_actual['rol_id']

    empresas = EmpresasService.obtener_todas()
    empresa_seleccionada = next((e for e in empresas if e['id'] == empresa_id), None)

    if not empresa_seleccionada:
        flash("La empresa seleccionada no existe.", "danger")
        return redirect(url_for('auth.seleccionar_empresa'))

    # Bloqueo para trabajadores si la empresa está operativamente INACTIVA
    if rol_id_global != 1 and empresa_seleccionada.get('estado') == 'Inactivo':
        flash("Acceso Denegado: Las operaciones de esta empresa han sido pausadas por el Administrador.", "danger")
        return redirect(url_for('auth.seleccionar_empresa'))

    # Bloqueo si la vinculación del trabajador específico está desvinculada
    vinculacion = UsuariosService.obtener_vinculacion_empresa(usuario_id, empresa_id)
    if rol_id_global != 1 and vinculacion.get('estado') == 'Desvinculado':
        flash("Acceso Denegado: Tu vinculación en esta empresa ha sido desactivada.", "danger")
        return redirect(url_for('auth.seleccionar_empresa'))

    # Asignar rol exclusivo de esta empresa para el usuario
    rol_especifico = vinculacion.get('rol_id', rol_id_global)
    session['usuario']['rol_id'] = rol_especifico

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
