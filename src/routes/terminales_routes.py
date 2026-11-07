from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.services.api_client import APIClient
from src.utils.decorators import requiere_rol

terminales_bp = Blueprint('terminales', __name__, url_prefix='/terminales')

@terminales_bp.route('/', methods=['GET'])
@requiere_rol(1, 2, 3)
def ver_terminales():
    """Muestra y permite configurar las terminales de pago (datáfonos Bold) y pasarelas (Wompi / Simulado)."""
    emp_id = session.get('empresa_activa', {}).get('id', 1)
    terminales, _ = APIClient.get('/terminales/', params={'empresa_id': emp_id})
    metodos_pago, _ = APIClient.get('/metodos_pago/', params={'empresa_id': emp_id})
    if not isinstance(terminales, list):
        terminales = []
    if not isinstance(metodos_pago, list):
        metodos_pago = []
    return render_template('terminales/ver_terminales.html', terminales=terminales, metodos_pago=metodos_pago)

@terminales_bp.route('/nueva', methods=['POST'])
@requiere_rol(1, 2, 3)
def nueva_terminal():
    """Crea una nueva terminal de pago (datáfono Bold o Simulado)."""
    emp_id = session.get('empresa_activa', {}).get('id', 1)
    serial = (request.form.get('terminal_serial') or request.form.get('codigo_terminal') or '').strip()
    modelo = (request.form.get('terminal_model') or request.form.get('ubicacion') or '').strip()
    email_usr = (request.form.get('email_usuario') or session.get('usuario', {}).get('email') or '').strip()
    data = {
        'nombre': request.form.get('nombre', '').strip(),
        'terminal_serial': serial,
        'terminal_model': modelo,
        'email_usuario': email_usr,
        'codigo_terminal': serial,
        'ubicacion': modelo,
        'proveedor': request.form.get('proveedor', 'simulado').strip(),
        'modo': request.form.get('modo', 'sandbox').strip(),
        'id_metodo_pago': int(request.form.get('id_metodo_pago')) if request.form.get('id_metodo_pago') else None,
        'id_empresa': emp_id,
        'estado': 'Activo'
    }
    res, err = APIClient.post('/terminales/', data=data)
    if err:
        flash(f"Error al crear terminal: {err}", "danger")
    else:
        flash(f"Terminal '{data['nombre']}' creada exitosamente.", "success")
    return redirect(url_for('terminales.ver_terminales'))

@terminales_bp.route('/editar/<int:id>', methods=['POST'])
@requiere_rol(1, 2, 3)
def editar_terminal(id):
    """Actualiza una terminal existente."""
    serial = (request.form.get('terminal_serial') or request.form.get('codigo_terminal') or '').strip()
    modelo = (request.form.get('terminal_model') or request.form.get('ubicacion') or '').strip()
    email_usr = (request.form.get('email_usuario') or '').strip()
    data = {
        'nombre': request.form.get('nombre', '').strip(),
        'terminal_serial': serial,
        'terminal_model': modelo,
        'codigo_terminal': serial,
        'ubicacion': modelo,
        'proveedor': request.form.get('proveedor', 'simulado').strip(),
        'modo': request.form.get('modo', 'sandbox').strip(),
        'estado': request.form.get('estado', 'Activo').strip()
    }
    if email_usr:
        data['email_usuario'] = email_usr
    if request.form.get('id_metodo_pago'):
        data['id_metodo_pago'] = int(request.form.get('id_metodo_pago'))
    res, err = APIClient.put(f'/terminales/{id}', data=data)
    if err:
        flash(f"Error al actualizar terminal: {err}", "danger")
    else:
        flash("Terminal actualizada correctamente.", "success")
    return redirect(url_for('terminales.ver_terminales'))

@terminales_bp.route('/pasarela/<int:id>', methods=['POST'])
@requiere_rol(1)
def configurar_pasarela(id):
    """Actualiza la configuración de pasarela (Bold / Wompi / Simulado) de un método de pago."""
    data = {
        'pasarela': request.form.get('pasarela', 'simulado').strip(),
        'modo': request.form.get('modo', 'sandbox').strip(),
        'api_key_publica': request.form.get('api_key_publica', '').strip()
    }
    if request.form.get('api_key_privada', '').strip():
        data['api_key_privada'] = request.form.get('api_key_privada', '').strip()
    if request.form.get('integrity_secret', '').strip():
        data['integrity_secret'] = request.form.get('integrity_secret', '').strip()
    if request.form.get('webhook_secret', '').strip():
        data['webhook_secret'] = request.form.get('webhook_secret', '').strip()

    res, err = APIClient.put(f'/metodos_pago/{id}', data=data)
    if err:
        flash(f"Error al actualizar pasarela: {err}", "danger")
    else:
        flash("Configuración de pasarela actualizada exitosamente.", "success")
    return redirect(url_for('terminales.ver_terminales'))
