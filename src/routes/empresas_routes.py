from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.services.empresas_service import EmpresasService
from src.services.facturas_service import FacturasService
from src.utils.decorators import requiere_rol

empresas_bp = Blueprint('empresas', __name__, url_prefix='/empresa')

@empresas_bp.route('/nueva', methods=['GET', 'POST'])
def nueva_empresa():
    """Formulario para crear y registrar una nueva empresa en la base de datos."""
    if request.method == 'POST':
        data = {
            'nombre': request.form.get('nombre'),
            'nit': request.form.get('nit'),
            'direccion': request.form.get('direccion'),
            'telefono': request.form.get('telefono'),
            'email': request.form.get('email'),
            'estado': 'Activo'
        }

        res, err = EmpresasService.crear(data)
        if err:
            flash(f"Error al registrar la empresa: {err}", "danger")
        else:
            flash("¡Nueva empresa registrada exitosamente en el sistema!", "success")
            return redirect(url_for('auth.seleccionar_empresa'))

    return render_template('empresas/nueva_empresa.html')

@empresas_bp.route('/configuracion', methods=['GET', 'POST'])
@requiere_rol(1) # Exclusivo para Administrador
def configuracion():
    """Formulario para actualizar los datos internos y el estado operativo de la empresa activa (Solo Admin)."""
    empresa_activa = session.get('empresa_activa')
    if not empresa_activa:
        flash("Debes seleccionar una empresa primero.", "warning")
        return redirect(url_for('auth.seleccionar_empresa'))

    empresa_id = empresa_activa['id']

    if request.method == 'POST':
        data = {
            'nombre': request.form.get('nombre'),
            'nit': request.form.get('nit'),
            'direccion': request.form.get('direccion'),
            'telefono': request.form.get('telefono'),
            'email': request.form.get('email')
        }

        res, err = EmpresasService.actualizar(empresa_id, data)
        if err:
            flash(f"Error al actualizar los datos de la empresa: {err}", "danger")
        else:
            session['empresa_activa']['nombre'] = data['nombre']
            session['empresa_activa']['nit'] = data['nit']
            flash("¡Datos de la empresa actualizados exitosamente!", "success")
            return redirect(url_for('empresas.configuracion'))

    datos_actuales = EmpresasService.obtener_por_id(empresa_id) or empresa_activa
    if isinstance(datos_actuales, dict) and 'empresa_activa' in session:
        session['empresa_activa'].update({
            k: v for k, v in datos_actuales.items()
            if k in (
                'nombre', 'nit', 'estado', 'plan_membresia', 'precio_membresia',
                'estado_membresia', 'membresia_activa', 'dias_restantes_membresia',
                'fecha_inicio_membresia', 'fecha_vencimiento_membresia'
            )
        })
        session.modified = True

    membresia_data = EmpresasService.obtener_membresia(empresa_id)
    metodos_pago = FacturasService.obtener_metodos_pago()
    terminales = FacturasService.obtener_terminales(solo_activas=True)

    return render_template(
        'empresas/configuracion.html',
        empresa=datos_actuales,
        membresia=membresia_data.get('membresia', {}),
        cobro_pendiente=membresia_data.get('cobro_pendiente'),
        pagos_membresia=membresia_data.get('historial_pagos', []),
        metodos_pago=metodos_pago,
        terminales=terminales
    )


@empresas_bp.route('/membresia/cobrar', methods=['POST'])
@requiere_rol(1)
def cobrar_membresia():
    """Inicia el cobro de la membresía empresarial por $19.900 COP."""
    empresa_activa = session.get('empresa_activa')
    if not empresa_activa:
        flash("Debes seleccionar una empresa primero.", "warning")
        return redirect(url_for('auth.seleccionar_empresa'))

    empresa_id = empresa_activa['id']
    modo_cobro = (request.form.get('modo_cobro') or 'link').strip().lower()
    meses = request.form.get('meses', 1, type=int) or 1

    payload = {'meses': max(1, min(12, meses))}
    if modo_cobro == 'terminal':
        payload['canal'] = 'datafono'
        id_terminal = request.form.get('id_terminal')
        if id_terminal and str(id_terminal).isdigit():
            payload['id_terminal'] = int(id_terminal)
    elif modo_cobro == 'manual':
        payload['canal'] = 'manual'
        referencia = (request.form.get('referencia_pago') or '').strip()
        if referencia:
            payload['referencia_pago'] = referencia
    else:
        payload['canal'] = 'link'
        id_metodo = request.form.get('id_metodo_pago')
        if id_metodo and str(id_metodo).isdigit():
            payload['id_metodo_pago'] = int(id_metodo)

    res, err = EmpresasService.iniciar_cobro_membresia(empresa_id, payload)
    if err:
        flash(f"Error al iniciar el cobro de membresía ($19.900 COP): {err}", "danger")
    else:
        cobro = res.get('cobro', {}) if isinstance(res, dict) else {}
        emp_actualizada = res.get('empresa') if isinstance(res, dict) else None
        if isinstance(emp_actualizada, dict) and 'empresa_activa' in session:
            session['empresa_activa'].update(emp_actualizada)
            session.modified = True

        ref = cobro.get('referencia') or ''
        if cobro.get('estado') == 'APROBADA':
            flash(f"✅ ¡Pago de membresía por $19.900 COP confirmado ({ref})! Membresía activa por 30 días.", "success")
        else:
            flash(
                f"📡 Cobro de membresía {ref} por $19.900 COP generado. "
                f"Abre el Checkout o usa 'Simular Aprobado' para activar los 30 días.",
                "info"
            )
    return redirect(url_for('empresas.configuracion') + '#membresia')


@empresas_bp.route('/membresia/simular/<int:cobro_id>', methods=['POST'])
@requiere_rol(1)
def simular_cobro_membresia(cobro_id):
    """Simula la aprobación o rechazo de un cobro de membresía ($19.900 COP) en modo Sandbox."""
    resultado_raw = (request.form.get('resultado') or 'APROBADA').upper()
    resultado = 'APROBADA' if resultado_raw in ('APPROVED', 'APROBADA') else 'RECHAZADA'
    res, err = EmpresasService.simular_cobro_membresia(cobro_id, resultado=resultado)
    if err:
        flash(f"Error al simular pago de membresía: {err}", "danger")
    else:
        emp_actualizada = res.get('empresa') if isinstance(res, dict) else None
        if isinstance(emp_actualizada, dict) and 'empresa_activa' in session:
            session['empresa_activa'].update(emp_actualizada)
            session.modified = True

        if resultado == 'APROBADA':
            flash("✅ ¡Membresía de $19.900 COP aprobada exitosamente! Tu empresa cuenta con 30 días adicionales de vigencia.", "success")
        else:
            flash("⚠️ El intento de cobro de membresía fue marcado como rechazado en el simulador.", "warning")
    return redirect(url_for('empresas.configuracion') + '#membresia')


@empresas_bp.route('/membresia/sincronizar/<int:cobro_id>', methods=['POST'])
@requiere_rol(1)
def sincronizar_cobro_membresia(cobro_id):
    """Consulta el estado actual de un cobro de membresía en la pasarela."""
    res, err = EmpresasService.consultar_cobro_membresia(cobro_id)
    if err:
        flash(f"No se pudo consultar el cobro de membresía: {err}", "warning")
    else:
        cobro = res.get('cobro', {}) if isinstance(res, dict) else {}
        emp_actualizada = res.get('empresa') if isinstance(res, dict) else None
        if isinstance(emp_actualizada, dict) and 'empresa_activa' in session:
            session['empresa_activa'].update(emp_actualizada)
            session.modified = True
        flash(f"🔄 Estado actualizado del cobro de membresía: {cobro.get('estado', 'PENDIENTE')}.", "info")
    return redirect(url_for('empresas.configuracion') + '#membresia')


@empresas_bp.route('/membresia/cancelar/<int:cobro_id>', methods=['POST'])
@requiere_rol(1)
def cancelar_cobro_membresia(cobro_id):
    """Cancela un cobro de membresía pendiente."""
    res, err = EmpresasService.cancelar_cobro_membresia(cobro_id)
    if err:
        flash(f"No se pudo cancelar el cobro de membresía: {err}", "warning")
    else:
        flash("🚫 Cobro de membresía pendiente cancelado.", "info")
    return redirect(url_for('empresas.configuracion') + '#membresia')

@empresas_bp.route('/cambiar_estado/<int:id>', methods=['POST'])
@requiere_rol(1) # Exclusivo para Administrador
def cambiar_estado(id):
    """Permite al Administrador desactivar o reactivar la empresa en la base de datos MySQL."""
    empresa = EmpresasService.obtener_por_id(id)
    if not empresa:
        flash("La empresa no existe.", "danger")
        return redirect(url_for('auth.seleccionar_empresa'))

    estado_actual = empresa.get('estado', 'Activo')
    nuevo_estado = 'Inactivo' if estado_actual == 'Activo' else 'Activo'

    res, err = EmpresasService.actualizar(id, {'estado': nuevo_estado})
    if err:
        flash(f"Error al cambiar el estado de la empresa: {err}", "danger")
    else:
        if 'empresa_activa' in session and session['empresa_activa']['id'] == id:
            session['empresa_activa']['estado'] = nuevo_estado
        
        flash(f"La empresa ha sido actualizada a estado: {nuevo_estado}", "info")

    return redirect(url_for('empresas.configuracion'))
