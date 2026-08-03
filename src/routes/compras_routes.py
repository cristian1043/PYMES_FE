from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.services.compras_service import ComprasService
from src.services.proveedores_service import ProveedoresService
from src.utils.decorators import requiere_rol

compras_bp = Blueprint('compras', __name__, url_prefix='/compras')

@compras_bp.route('/', methods=['GET'])
@requiere_rol(1, 3)
def ver_compras():
    """Muestra la lista de compras registradas (Admin y Almacenista)."""
    compras = ComprasService.obtener_todas()
    return render_template('compras/ver_compras.html', compras=compras)

@compras_bp.route('/nueva', methods=['GET', 'POST'])
@requiere_rol(1, 3)
def nueva_compra():
    """Formulario y registro de una nueva compra (Admin y Almacenista)."""
    if request.method == 'POST':
        subtotal = float(request.form.get('subtotal', 0))
        iva = float(request.form.get('iva', 0))
        descuento = float(request.form.get('descuento', 0))
        total = subtotal + iva - descuento

        data = {
            'numero': request.form.get('numero'),
            'subtotal': subtotal,
            'iva': iva,
            'descuento': descuento,
            'total': total,
            'id_proveedor': int(request.form.get('id_proveedor')),
            'id_usuario': 1
        }
        res, err = ComprasService.crear(data)
        if err:
            flash(f"Error al registrar la compra: {err}", "danger")
        else:
            flash("Compra registrada exitosamente", "success")
            return redirect(url_for('compras.ver_compras'))

    proveedores = ProveedoresService.obtener_todos()
    return render_template('compras/nueva_compra.html', proveedores=proveedores)
