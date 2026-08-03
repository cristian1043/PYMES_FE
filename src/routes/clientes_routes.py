from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.services.clientes_service import ClientesService

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@clientes_bp.route('/', methods=['GET'])
def ver_clientes():
    """Muestra la tabla con la lista de clientes."""
    clientes = ClientesService.obtener_todos()
    return render_template('clientes/ver_clientes.html', clientes=clientes)

@clientes_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    """Formulario y acción para crear un nuevo cliente."""
    if request.method == 'POST':
        data = {
            'nombre': request.form.get('nombre'),
            'apellido': request.form.get('apellido'),
            'email': request.form.get('email'),
            'telefono': request.form.get('telefono'),
            'direccion': request.form.get('direccion'),
            'cedula_runc': request.form.get('cedula_runc')
        }
        res, err = ClientesService.crear(data)
        if err:
            flash(f"Error al crear el cliente: {err}", "danger")
        else:
            flash("Cliente creado exitosamente", "success")
            return redirect(url_for('clientes.ver_clientes'))
            
    return render_template('clientes/nuevo_cliente.html')
