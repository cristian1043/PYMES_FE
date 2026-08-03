from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.services.clientes_service import ClientesService
from src.utils.decorators import requiere_rol

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@clientes_bp.route('/', methods=['GET'])
@requiere_rol(1, 2) # Admin y Vendedor
def ver_clientes():
    """Lista los clientes registrados (Admin y Vendedor)."""
    clientes = ClientesService.obtener_todos()
    return render_template('clientes/ver_clientes.html', clientes=clientes)

@clientes_bp.route('/nuevo', methods=['GET', 'POST'])
@requiere_rol(1, 2) # Admin y Vendedor
def nuevo_cliente():
    """Formulario para agregar un cliente (Admin y Vendedor)."""
    if request.method == 'POST':
        data = {
            'tipo_documento': request.form.get('tipo_documento'),
            'documento': request.form.get('documento'),
            'nombre': request.form.get('nombre'),
            'apellido': request.form.get('apellido'),
            'email': request.form.get('email'),
            'telefono': request.form.get('telefono'),
            'direccion': request.form.get('direccion')
        }
        res, err = ClientesService.crear(data)
        if err:
            flash(f"Error al crear el cliente: {err}", "danger")
        else:
            flash("Cliente creado exitosamente", "success")
            return redirect(url_for('clientes.ver_clientes'))

    return render_template('clientes/nuevo_cliente.html')
