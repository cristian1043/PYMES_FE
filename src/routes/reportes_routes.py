from flask import Blueprint, render_template, request
from src.services.reportes_service import ReportesService
from src.utils.decorators import requiere_rol
import math

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@reportes_bp.route('/ventas', methods=['GET'])
@requiere_rol(1)
def reporte_ventas():
    """Muestra el resumen ejecutivo de ventas y facturación con paginación (Solo Admin)."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    resumen = ReportesService.obtener_reporte_ventas()
    facturas_todas = resumen.get('facturas', []) if isinstance(resumen, dict) else []
    
    total = len(facturas_todas)
    total_pages = max(1, math.ceil(total / per_page))
    facturas_paginadas = facturas_todas[(page - 1) * per_page : page * per_page]
    
    paginacion = {'page': page, 'per_page': per_page, 'total_pages': total_pages, 'total': total}
    return render_template('reportes/reporte_ventas.html', resumen=resumen, facturas=facturas_paginadas, paginacion=paginacion)

@reportes_bp.route('/clientes', methods=['GET'])
@requiere_rol(1)
def reporte_clientes():
    """Muestra el ranking y análisis de compras por cliente con paginación (Solo Admin)."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    clientes_todos = ReportesService.obtener_reporte_clientes()
    if not isinstance(clientes_todos, list):
        clientes_todos = []

    total = len(clientes_todos)
    total_pages = max(1, math.ceil(total / per_page))
    clientes_paginados = clientes_todos[(page - 1) * per_page : page * per_page]

    paginacion = {'page': page, 'per_page': per_page, 'total_pages': total_pages, 'total': total}
    return render_template('reportes/reporte_clientes.html', clientes=clientes_paginados, paginacion=paginacion)

@reportes_bp.route('/inventario', methods=['GET'])
@requiere_rol(1, 3)
def reporte_inventario():
    """Muestra la valoración de inventario y estado de stock con paginación (Admin y Almacenista)."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    inventario = ReportesService.obtener_reporte_inventario()
    productos_todos = inventario.get('productos', []) if isinstance(inventario, dict) else []

    total = len(productos_todos)
    total_pages = max(1, math.ceil(total / per_page))
    productos_paginados = productos_todos[(page - 1) * per_page : page * per_page]

    paginacion = {'page': page, 'per_page': per_page, 'total_pages': total_pages, 'total': total}
    return render_template('reportes/reporte_inventario.html', inventario=inventario, productos=productos_paginados, paginacion=paginacion)
