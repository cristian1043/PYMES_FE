from src.services.api_client import APIClient

class FacturasService:
    """
    Servicio para consumir la API de facturación y métodos de pago del Backend.
    """

    @staticmethod
    def obtener_todas():
        """Obtiene la lista completa de facturas."""
        data, error = APIClient.get('/facturas/')
        if error:
            print(f"Error al obtener facturas: {error}")
            return []
        return data if data is not None else []

    @staticmethod
    def obtener_por_id(factura_id):
        """Obtiene los detalles de una factura específica por su ID."""
        data, error = APIClient.get(f'/facturas/{factura_id}')
        if error:
            print(f"Error al obtener factura {factura_id}: {error}")
            return None
        return data

    @staticmethod
    def crear(datos_factura):
        """Crea una nueva factura de venta."""
        return APIClient.post('/facturas/', data=datos_factura)

    @staticmethod
    def actualizar(factura_id, datos_factura):
        """Actualiza una factura existente."""
        return APIClient.put(f'/facturas/{factura_id}', data=datos_factura)

    @staticmethod
    def eliminar(factura_id):
        """Elimina una factura por su ID."""
        return APIClient.delete(f'/facturas/{factura_id}')

    @staticmethod
    def obtener_metodos_pago():
        """Obtiene la lista de métodos de pago disponbiles (Efectivo, Tarjeta, Transferencia, etc.)."""
        data, error = APIClient.get('/metodos_pago/')
        if error:
            print(f"Error al obtener métodos de pago: {error}")
            return []
        return data if data is not None else []
