import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.services.facturas_service import FacturasService
from src.services.clientes_service import ClientesService
from src.services.productos_service import ProductosService
from src.utils.decorators import requiere_rol

facturas_bp = Blueprint('facturas', __name__, url_prefix='/facturas')

@facturas_bp.route('/', methods=['GET'])
@requiere_rol(1, 2, 3)
def ver_facturas():
    """Lista las facturas de venta con paginación."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    res_paginado = FacturasService.obtener_todas(page=page, per_page=per_page)

    items = res_paginado.get("items", []) if isinstance(res_paginado, dict) else (res_paginado if isinstance(res_paginado, list) else [])
    return render_template('facturas/ver_facturas.html', facturas=items, paginacion=res_paginado)

@facturas_bp.route('/nueva', methods=['GET', 'POST'])
@requiere_rol(1, 2, 3)
def nueva_factura():
    """Formulario y procesamiento de una nueva factura de venta con detalles dinámicos y correlativo automático."""
    metodos_pago = FacturasService.obtener_metodos_pago()
    terminales = FacturasService.obtener_terminales(solo_activas=True)
    siguiente_numero = FacturasService.obtener_siguiente_numero()

    if request.method == 'POST':
        usuario_id = session.get('usuario', {}).get('id', 1)
        empresa_id = session.get('empresa_activa', {}).get('id', 1)

        detalles = []
        raw_detalles = request.form.get('detalles_json')
        if raw_detalles:
            try:
                detalles = json.loads(raw_detalles)
            except Exception as e:
                print(f"Error al decodificar detalles_json: {e}")

        id_cliente_raw = (request.form.get('id_cliente') or '').strip()
        id_cliente_int = int(id_cliente_raw) if id_cliente_raw.isdigit() else None

        id_mp_raw = (request.form.get('id_metodo_pago') or '1').strip()
        id_metodo_pago = int(id_mp_raw) if id_mp_raw.isdigit() else 1
        metodo_nombre = (request.form.get('metodo_pago_nombre') or '').strip()
        referencia_pago = (request.form.get('referencia_pago') or '').strip() or None
        accion_pasarela = (request.form.get('accion_pasarela') or 'aprobar_inmediato').strip()
        id_terminal_raw = (request.form.get('id_terminal') or '').strip()

        data = {
            'numero': request.form.get('numero') or siguiente_numero,
            'subtotal': float(request.form.get('subtotal', 0)),
            'iva': float(request.form.get('iva', 0)),
            'descuento': float(request.form.get('descuento', 0)),
            'total': float(request.form.get('total', 0)),
            'id_metodo_pago': id_metodo_pago,
            'metodo_pago': metodo_nombre or None,
            'referencia_pago': referencia_pago,
            'aprobar_inmediato': (accion_pasarela == 'aprobar_inmediato'),
            'id_usuario': usuario_id,
            'id_empresa': empresa_id,
            'detalles': detalles
        }

        if id_cliente_int:
            data['id_cliente'] = id_cliente_int
        else:
            data['cliente_nombre'] = (request.form.get('cliente_nombre') or 'Consumidor Final').strip()
            data['documento_cliente'] = (request.form.get('documento_cliente') or '222222222222').strip()
            data['tipo_documento'] = (request.form.get('tipo_documento') or 'CC').strip()

        res, err = FacturasService.crear(data)
        if err:
            flash(f"Error al registrar la venta / factura: {err}", "danger")
        else:
            factura_id = res.get('id') if isinstance(res, dict) else None
            if factura_id:
                # Si eligió iniciar cobro en terminal o link de pasarela
                metodo_obj = next((m for m in metodos_pago if str(m.get('id')) == str(id_metodo_pago)), {})
                es_integrado = bool(metodo_obj.get('integrado') or str(metodo_obj.get('pasarela', '')).lower() in ('bold', 'wompi', 'simulado'))
                if es_integrado and accion_pasarela == 'enviar_cobro':
                    es_link = (str(metodo_obj.get('tipo', '')).lower() == 'pasarela' or str(metodo_obj.get('pasarela', '')).lower() == 'wompi')
                    cobro_payload = {
                        'canal': 'link' if es_link else 'datafono',
                        'id_metodo_pago': id_metodo_pago
                    }
                    if not es_link and id_terminal_raw.isdigit():
                        cobro_payload['id_terminal'] = int(id_terminal_raw)
                    FacturasService.crear_cobro(factura_id, cobro_payload)
                    flash("📡 Venta registrada y orden de cobro enviada a la terminal / pasarela.", "info")
                else:
                    flash("✅ ¡Venta y factura registrada y pagada exitosamente!", "success")
                return redirect(url_for('facturas.detalle_factura', id=factura_id))
            flash("✅ Venta y factura emitida exitosamente.", "success")
            return redirect(url_for('facturas.ver_facturas'))

    clientes_res = ClientesService.obtener_todos(per_page=1000)
    clientes = clientes_res.get("items", []) if isinstance(clientes_res, dict) else (clientes_res if isinstance(clientes_res, list) else [])
    
    productos_res = ProductosService.obtener_todos(page=1, per_page=500)
    productos = productos_res.get("items", []) if isinstance(productos_res, dict) else (productos_res if isinstance(productos_res, list) else [])

    return render_template(
        'facturas/nueva_factura.html',
        clientes=clientes,
        metodos_pago=metodos_pago,
        terminales=terminales,
        productos=productos,
        siguiente_numero=siguiente_numero
    )

@facturas_bp.route('/cancelar/<int:id>', methods=['POST'])
@requiere_rol(1, 2, 3)
def cancelar_factura(id):
    """Cancela una factura emitida y restablece el stock de inventario."""
    res, err = FacturasService.cancelar(id)
    if err:
        flash(f"Error al cancelar la factura: {err}", "danger")
    else:
        flash("Factura cancelada correctamente y stock restablecido", "success")
    return redirect(url_for('facturas.ver_facturas'))

@facturas_bp.route('/cobrar/<int:id>', methods=['POST'])
@requiere_rol(1, 2, 3)
def cobrar_factura(id):
    """Inicia un cobro en terminal (datáfono Bold), link de pago (Wompi / Simulado) o registra pago manual."""
    modo_cobro = request.form.get('modo_cobro', 'terminal')
    if modo_cobro == 'manual':
        id_metodo = request.form.get('id_metodo_pago')
        referencia = request.form.get('referencia_pago')
        payload = {}
        if id_metodo and str(id_metodo).isdigit():
            payload['id_metodo_pago'] = int(id_metodo)
        if referencia:
            payload['referencia_pago'] = referencia
        res, err = FacturasService.pagar_manual(id, payload)
        if err:
            flash(f"No se pudo registrar el pago manual: {err}", "danger")
        else:
            flash("✅ Pago directo en caja registrado y factura marcada como Pagada.", "success")
        return redirect(url_for('facturas.detalle_factura', id=id))

    if modo_cobro == 'terminal':
        id_terminal = request.form.get('id_terminal')
        payload = {'canal': 'datafono'}
        if id_terminal and str(id_terminal).isdigit():
            payload['id_terminal'] = int(id_terminal)
    else:
        id_metodo = request.form.get('id_metodo_pago')
        payload = {'canal': 'link'}
        if id_metodo and str(id_metodo).isdigit():
            payload['id_metodo_pago'] = int(id_metodo)

    res, err = FacturasService.crear_cobro(id, payload)
    if err:
        flash(f"Error al iniciar el cobro en pasarela/terminal: {err}", "danger")
    else:
        cobro = res.get('cobro', {}) if isinstance(res, dict) else {}
        ref = cobro.get('referencia') or cobro.get('referencia_interna', '')
        flash(f"📡 Cobro {ref} enviado a pasarela/terminal. Usa 'Simular Aprobado' o abre el Checkout para confirmar.", "info")
    return redirect(url_for('facturas.detalle_factura', id=id))

@facturas_bp.route('/simular_cobro/<int:cobro_id>', methods=['POST'])
@requiere_rol(1, 2, 3)
def simular_cobro(cobro_id):
    """Simula la aprobación o rechazo de un cobro en modo pruebas (Sandbox / Simulado)."""
    factura_id = request.form.get('id_factura', type=int)
    resultado_raw = (request.form.get('resultado') or 'APROBADA').upper()
    resultado = 'APROBADA' if resultado_raw in ('APPROVED', 'APROBADA') else 'RECHAZADA'
    res, err = FacturasService.simular_cobro(cobro_id, resultado=resultado)
    if err:
        flash(f"Error al simular respuesta de pasarela: {err}", "danger")
    else:
        if resultado == 'APROBADA':
            flash("✅ ¡Pago aprobado en pasarela/datáfono! La factura ha quedado liquidada como Pagada.", "success")
        else:
            flash("⚠️ Cobro marcado como rechazado en el simulador. Puedes iniciar un nuevo intento.", "warning")
    if factura_id:
        return redirect(url_for('facturas.detalle_factura', id=factura_id))
    return redirect(url_for('facturas.ver_facturas'))

@facturas_bp.route('/sincronizar_cobro/<int:cobro_id>', methods=['POST'])
@requiere_rol(1, 2, 3)
def sincronizar_cobro(cobro_id):
    """Consulta el estado actual del cobro contra la pasarela."""
    factura_id = request.form.get('id_factura', type=int)
    res, err = FacturasService.consultar_cobro(cobro_id)
    if err:
        flash(f"No se pudo consultar el cobro: {err}", "warning")
    else:
        cobro = res.get('cobro', {}) if isinstance(res, dict) else {}
        flash(f"🔄 Estado actualizado del cobro: {cobro.get('estado', 'PENDIENTE')}.", "info")
    if factura_id:
        return redirect(url_for('facturas.detalle_factura', id=factura_id))
    return redirect(url_for('facturas.ver_facturas'))

@facturas_bp.route('/detalle/<int:id>', methods=['GET'])
@requiere_rol(1, 2, 3)
def detalle_factura(id):
    """Muestra el detalle, recibo y panel de cobro con terminal/pasarela de una factura específica."""
    factura = FacturasService.obtener_por_id(id)
    if not factura or not isinstance(factura, dict):
        flash("La factura solicitada no existe", "warning")
        return redirect(url_for('facturas.ver_facturas'))

    cliente = factura.get('cliente') if isinstance(factura.get('cliente'), dict) else {}
    usuario = factura.get('usuario') if isinstance(factura.get('usuario'), dict) else {}
    mp_raw = factura.get('metodo_pago_detalle') or factura.get('metodo_pago')
    metodo_pago = mp_raw if isinstance(mp_raw, dict) else {'nombre': str(mp_raw or 'Efectivo')}
    detalles = factura.get('detalles') if isinstance(factura.get('detalles'), list) else []

    factura['cliente'] = {
        'nombre': cliente.get('nombre', factura.get('cliente_nombre', 'Cliente Comercial')),
        'apellido': cliente.get('apellido', ''),
        'tipo_documento': cliente.get('tipo_documento', factura.get('cliente_tipo_documento', 'CC')),
        'documento': cliente.get('documento', factura.get('cliente_documento', '1015432109')),
        'email': cliente.get('email', 'cliente@correo.com'),
        'telefono': cliente.get('telefono', '3001234567'),
        'direccion': cliente.get('direccion', 'Calle 45 # 12-34')
    }

    factura['usuario'] = {
        'nombre': usuario.get('nombre', 'Cristian'),
        'apellido': usuario.get('apellido', 'García'),
        'email': usuario.get('email', 'cristian@pymes.com')
    }

    factura['metodo_pago'] = {
        'id': metodo_pago.get('id', factura.get('id_metodo_pago', 1)),
        'nombre': metodo_pago.get('nombre', 'Efectivo'),
        'pasarela': metodo_pago.get('pasarela', 'ninguna'),
        'integrado': metodo_pago.get('integrado', False)
    }

    factura['detalles'] = detalles

    terminales = FacturasService.obtener_terminales(solo_activas=True)
    metodos_pago = FacturasService.obtener_metodos_pago()
    cobros = FacturasService.obtener_cobros(id)

    return render_template(
        'facturas/detalle_factura.html',
        factura=factura,
        terminales=terminales,
        metodos_pago=metodos_pago,
        cobros=cobros
    )
