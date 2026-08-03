from src.services.api_client import APIClient

class ReportesService:
    """
    Servicio Frontend encardado únicamente de consumir los endpoints
    de reportes procesados por la Lógica de Negocio del Backend.
    """

    @staticmethod
    def obtener_reporte_ventas():
        """Consume el reporte financiero de ventas procesado por el Backend."""
        data, error = APIClient.get('/reportes/ventas')
        if error or not data:
            return {
                'total_ventas': 0.0,
                'subtotal': 0.0,
                'iva': 0.0,
                'descuento': 0.0,
                'cantidad_facturas': 0,
                'promedio_venta': 0.0,
                'facturas': []
            }
        return data

    @staticmethod
    def obtener_reporte_clientes():
        """Consume el ranking comercial de clientes procesado por el Backend."""
        data, error = APIClient.get('/reportes/clientes')
        if error or not data:
            return []
        return data

    @staticmethod
    def obtener_reporte_inventario():
        """Consume la valoración de inventario y stock procesada por el Backend."""
        data, error = APIClient.get('/reportes/inventario')
        if error or not data:
            return {
                'valor_total_inventario': 0.0,
                'total_productos': 0,
                'productos_bajo_stock': 0,
                'productos': []
            }
        return data
