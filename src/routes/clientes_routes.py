from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.services.clientes_service import ClientesService
from src.utils.decorators import requiere_rol

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@clientes_bp.route('/', methods=['GET'])
@requiere_rol(1, 2) # Admin y Vendedor
def ver_clientes():
    """Lista los clientes registrados con paginación (Admin y Vendedor)."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    res_paginado = ClientesService.obtener_todos(page=page, per_page=per_page)

    items = res_paginado.get("items", []) if isinstance(res_paginado, dict) else res_paginado
    return render_template('clientes/ver_clientes.html', clientes=items, paginacion=res_paginado)

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

@clientes_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@requiere_rol(1, 2) # Admin y Vendedor
def editar_cliente(id):
    """Formulario y procesamiento para actualizar la información de un cliente."""
    cliente = ClientesService.obtener_por_id(id)
    if not cliente:
        flash("El cliente especificado no existe", "warning")
        return redirect(url_for('clientes.ver_clientes'))

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
        res, err = ClientesService.actualizar(id, data)
        if err:
            flash(f"Error al actualizar el cliente: {err}", "danger")
        else:
            flash("Cliente actualizado exitosamente", "success")
            return redirect(url_for('clientes.ver_clientes'))

    return render_template('clientes/editar_cliente.html', cliente=cliente)
