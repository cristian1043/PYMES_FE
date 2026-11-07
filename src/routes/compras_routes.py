from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.services.compras_service import ComprasService
from src.services.proveedores_service import ProveedoresService
from src.utils.decorators import requiere_rol

compras_bp = Blueprint('compras', __name__, url_prefix='/compras')

@compras_bp.route('/', methods=['GET'])
@requiere_rol(1, 2, 3)
def ver_compras():
    """Muestra la lista de compras registradas con paginación."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    res_paginado = ComprasService.obtener_todas(page=page, per_page=per_page)

    items = res_paginado.get("items", []) if isinstance(res_paginado, dict) else (res_paginado if isinstance(res_paginado, list) else [])
    return render_template('compras/ver_compras.html', compras=items, paginacion=res_paginado)

@compras_bp.route('/nueva', methods=['GET', 'POST'])
@requiere_rol(1, 2, 3)
def nueva_compra():
    """Formulario interactivo y registro de orden de compra con actualización de inventario."""
    from src.services.productos_service import ProductosService
    from src.services.facturas_service import FacturasService
    import json

    siguiente_numero = ComprasService.obtener_siguiente_numero()
    metodos_res = FacturasService.obtener_metodos_pago()
    metodos_pago = metodos_res if isinstance(metodos_res, list) else (metodos_res.get("items", []) if isinstance(metodos_res, dict) else [])

    if request.method == 'POST':
        usuario_id = session.get('usuario', {}).get('id', 1)
        empresa_id = session.get('empresa_activa', {}).get('id', 1)
        detalles_json = request.form.get('detalles_json', '[]')
        
        try:
            detalles_items = json.loads(detalles_json)
        except Exception:
            detalles_items = []

        id_mp_raw = request.form.get('id_metodo_pago') or 1
        metodo_nombre = (request.form.get('metodo_pago') or '').strip()
        try:
            id_mp_int = int(id_mp_raw)
        except ValueError:
            id_mp_int = 1
            if not metodo_nombre:
                metodo_nombre = str(id_mp_raw).strip()

        if not metodo_nombre:
            for m in metodos_pago:
                if str(m.get('id')) == str(id_mp_int):
                    metodo_nombre = m.get('nombre', 'Efectivo')
                    break
        if not metodo_nombre:
            metodo_nombre = 'Efectivo'

        data = {
            'numero': request.form.get('numero') or siguiente_numero,
            'subtotal': float(request.form.get('subtotal', 0)),
            'iva': float(request.form.get('iva', 0)),
            'descuento': float(request.form.get('descuento', 0)),
            'total': float(request.form.get('total', 0)),
            'id_proveedor': int(request.form.get('id_proveedor', 1)),
            'id_metodo_pago': id_mp_int,
            'metodo_pago': metodo_nombre,
            'referencia_pago': (request.form.get('referencia_pago') or '').strip() or None,
            'id_usuario': usuario_id,
            'id_empresa': empresa_id,
            'detalles': detalles_items
        }

        res, err = ComprasService.crear(data)
        if err:
            flash(f"Error al registrar la compra: {err}", "danger")
        else:
            flash(f"Orden de compra {data['numero']} registrada exitosamente ({metodo_nombre}) y stock actualizado.", "success")
            return redirect(url_for('compras.ver_compras'))

    prov_res = ProveedoresService.obtener_todos(per_page=1000)
    proveedores = prov_res.get("items", []) if isinstance(prov_res, dict) else (prov_res if isinstance(prov_res, list) else [])
    
    prods_res = ProductosService.obtener_todos(per_page=1000)
    productos = prods_res.get("items", []) if isinstance(prods_res, dict) else (prods_res if isinstance(prods_res, list) else [])

    return render_template('compras/nueva_compra.html', proveedores=proveedores, productos=productos, metodos_pago=metodos_pago, siguiente_numero=siguiente_numero)

@compras_bp.route('/cancelar/<int:id>', methods=['POST'])
@requiere_rol(1, 2, 3)
def cancelar_compra(id):
    """Cancela una compra y revierte el stock acumulado."""
    res, err = ComprasService.cancelar(id)
    if err:
        flash(f"Error al cancelar la compra: {err}", "danger")
    else:
        flash("La orden de compra ha sido cancelada y el stock fue restituido.", "info")
    return redirect(url_for('compras.ver_compras'))

@compras_bp.route('/detalle/<int:id>', methods=['GET'])
@requiere_rol(1, 2, 3)
def detalle_compra(id):
    """Muestra el detalle y comprobante de una compra de inventario específica."""
    compra = ComprasService.obtener_por_id(id)
    if not compra or not isinstance(compra, dict):
        flash("La compra solicitada no existe", "warning")
        return redirect(url_for('compras.ver_compras'))

    proveedor = compra.get('proveedor') if isinstance(compra.get('proveedor'), dict) else {}
    usuario = compra.get('usuario') if isinstance(compra.get('usuario'), dict) else {}
    detalles = compra.get('detalles') if isinstance(compra.get('detalles'), list) else []

    compra['proveedor'] = {
        'nombre': proveedor.get('nombre', 'Mayorista Tecnológico de Colombia'),
        'nit': proveedor.get('nit', '900111222-3'),
        'telefono': proveedor.get('telefono', '6014445566'),
        'email': proveedor.get('email', 'ventas@mayortecno.com'),
        'direccion': proveedor.get('direccion', 'Calle 26 # 69-76')
    }

    compra['usuario'] = {
        'nombre': usuario.get('nombre', 'Carlos'),
        'apellido': usuario.get('apellido', 'Rodríguez'),
        'email': usuario.get('email', 'carlos@pymes.com')
    }

    compra['detalles'] = detalles

    return render_template('compras/detalle_compra.html', compra=compra)
