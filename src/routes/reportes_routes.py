from flask import Blueprint, render_template
from src.services.reportes_service import ReportesService
from src.utils.decorators import requiere_rol

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@reportes_bp.route('/ventas', methods=['GET'])
@requiere_rol(1)
def reporte_ventas():
    """Muestra el resumen ejecutivo de ventas y facturación (Solo Admin)."""
    resumen = ReportesService.obtener_reporte_ventas()
    return render_template('reportes/reporte_ventas.html', resumen=resumen)

@reportes_bp.route('/clientes', methods=['GET'])
@requiere_rol(1)
def reporte_clientes():
    """Muestra el ranking y análisis de compras por cliente (Solo Admin)."""
    clientes_reporte = ReportesService.obtener_reporte_clientes()
    return render_template('reportes/reporte_clientes.html', clientes=clientes_reporte)

@reportes_bp.route('/inventario', methods=['GET'])
@requiere_rol(1, 3)
def reporte_inventario():
    """Muestra la valoración de inventario y estado de stock (Admin y Almacenista)."""
    inventario = ReportesService.obtener_reporte_inventario()
    return render_template('reportes/reporte_inventario.html', inventario=inventario)
