from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.services.empresas_service import EmpresasService
from src.utils.decorators import requiere_rol

empresas_bp = Blueprint('empresas', __name__, url_prefix='/empresa')

@empresas_bp.route('/configuracion', methods=['GET', 'POST'])
@requiere_rol(1) # Exclusivo para Administrador
def configuracion():
    """Formulario para actualizar los datos internos de la empresa activa (Solo Admin)."""
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
