from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.services.proveedores_service import ProveedoresService
from src.utils.decorators import requiere_rol

proveedores_bp = Blueprint('proveedores', __name__, url_prefix='/proveedores')

@proveedores_bp.route('/', methods=['GET'])
@requiere_rol(1, 3) # Admin y Almacenista
def ver_proveedores():
    """Lista de proveedores con soporte para paginación (Admin y Almacenista)."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    res_paginado = ProveedoresService.obtener_todos(page=page, per_page=per_page)

    items = res_paginado.get("items", []) if isinstance(res_paginado, dict) else res_paginado
    return render_template('proveedores/ver_proveedores.html', proveedores=items, paginacion=res_paginado)

@proveedores_bp.route('/nuevo', methods=['GET', 'POST'])
@requiere_rol(1, 3) # Admin y Almacenista
def nuevo_proveedor():
    """Formulario para agregar un nuevo proveedor (Admin y Almacenista)."""
    if request.method == 'POST':
        data = {
            'nombre': request.form.get('nombre'),
            'nit': request.form.get('nit'),
            'contacto': request.form.get('contacto'),
            'telefono': request.form.get('telefono'),
            'email': request.form.get('email'),
            'direccion': request.form.get('direccion')
        }
        res, err = ProveedoresService.crear(data)
        if err:
            flash(f"Error al crear el proveedor: {err}", "danger")
        else:
            flash("Proveedor registrado exitosamente", "success")
            return redirect(url_for('proveedores.ver_proveedores'))

    return render_template('proveedores/nuevo_proveedor.html')

@proveedores_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@requiere_rol(1, 3) # Admin y Almacenista
def editar_proveedor(id):
    """Formulario y procesamiento para actualizar la información de un proveedor."""
    proveedor = ProveedoresService.obtener_por_id(id)
    if not proveedor:
        flash("El proveedor especificado no existe", "warning")
        return redirect(url_for('proveedores.ver_proveedores'))

    if request.method == 'POST':
        data = {
            'nombre': request.form.get('nombre'),
            'nit': request.form.get('nit'),
            'contacto': request.form.get('contacto'),
            'telefono': request.form.get('telefono'),
            'email': request.form.get('email'),
            'direccion': request.form.get('direccion')
        }
        res, err = ProveedoresService.actualizar(id, data)
        if err:
            flash(f"Error al actualizar el proveedor: {err}", "danger")
        else:
            flash("Proveedor actualizado exitosamente", "success")
            return redirect(url_for('proveedores.ver_proveedores'))

    return render_template('proveedores/editar_proveedor.html', proveedor=proveedor)
