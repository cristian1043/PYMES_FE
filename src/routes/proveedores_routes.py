from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.services.proveedores_service import ProveedoresService

proveedores_bp = Blueprint('proveedores', __name__, url_prefix='/proveedores')

@proveedores_bp.route('/', methods=['GET'])
def ver_proveedores():
    """Muestra la tabla con la lista de proveedores."""
    proveedores = ProveedoresService.obtener_todos()
    return render_template('proveedores/ver_proveedores.html', proveedores=proveedores)

@proveedores_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo_proveedor():
    """Formulario para registrar un nuevo proveedor."""
    if request.method == 'POST':
        data = {
            'nit': request.form.get('nit'),
            'nombre': request.form.get('nombre'),
            'telefono': request.form.get('telefono'),
            'direccion': request.form.get('direccion'),
            'email': request.form.get('email')
        }
        res, err = ProveedoresService.crear(data)
        if err:
            flash(f"Error al registrar el proveedor: {err}", "danger")
        else:
            flash("Proveedor registrado exitosamente", "success")
            return redirect(url_for('proveedores.ver_proveedores'))

    return render_template('proveedores/nuevo_proveedor.html')
