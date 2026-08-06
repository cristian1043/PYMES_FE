from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.services.empresas_service import EmpresasService
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
    return render_template('empresas/configuracion.html', empresa=datos_actuales)

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
