from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.services.facturas_service import FacturasService
from src.services.clientes_service import ClientesService
from src.utils.decorators import requiere_rol

facturas_bp = Blueprint('facturas', __name__, url_prefix='/facturas')

@facturas_bp.route('/', methods=['GET'])
@requiere_rol(1, 2) # Admin y Vendedor
def ver_facturas():
    """Lista las facturas de venta (Admin y Vendedor)."""
    facturas = FacturasService.obtener_todas()
    return render_template('facturas/ver_facturas.html', facturas=facturas)

@facturas_bp.route('/nueva', methods=['GET', 'POST'])
@requiere_rol(1, 2) # Admin y Vendedor
def nueva_factura():
    """Formulario y procesamiento de una nueva factura delegando el cálculo de totales al Backend."""
    if request.method == 'POST':
        usuario_id = session.get('usuario', {}).get('id', 1)

        data = {
            'numero': request.form.get('numero'),
            'subtotal': float(request.form.get('subtotal', 0)),
            'iva': float(request.form.get('iva', 0)),
            'descuento': float(request.form.get('descuento', 0)),
            'id_cliente': int(request.form.get('id_cliente')),
            'id_metodo_pago': int(request.form.get('id_metodo_pago')),
            'id_usuario': usuario_id
        }

        res, err = FacturasService.crear(data)
        if err:
            flash(f"Error al emitir la factura: {err}", "danger")
        else:
            flash("Factura emitida exitosamente", "success")
            return redirect(url_for('facturas.ver_facturas'))

    clientes = ClientesService.obtener_todos()
    metodos_pago = FacturasService.obtener_metodos_pago()
    return render_template('facturas/nueva_factura.html', clientes=clientes, metodos_pago=metodos_pago)

@facturas_bp.route('/detalle/<int:id>', methods=['GET'])
@requiere_rol(1, 2)
def detalle_factura(id):
    """Muestra el detalle y recibo de una factura específica."""
    factura = FacturasService.obtener_por_id(id)
    if not factura:
        flash("La factura solicitada no existe", "warning")
        return redirect(url_for('facturas.ver_facturas'))
    return render_template('facturas/detalle_factura.html', factura=factura)
