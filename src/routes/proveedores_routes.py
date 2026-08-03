from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.services.proveedores_service import ProveedoresService
from src.utils.decorators import requiere_rol

proveedores_bp = Blueprint('proveedores', __name__, url_prefix='/proveedores')

@proveedores_bp.route('/', methods=['GET'])
@requiere_rol(1, 3) # Admin y Almacenista
def ver_proveedores():
    """Lista de proveedores (Admin y Almacenista)."""
    proveedores = ProveedoresService.obtener_todos()
    return render_template('proveedores/ver_proveedores.html', proveedores=proveedores)

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
