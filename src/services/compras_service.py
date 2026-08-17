from src.services.api_client import APIClient

class ComprasService:
    """
    Servicio para consumir la API de compras del Backend.
    """

    @staticmethod
    def obtener_todas(page=1, per_page=10):
        """Obtiene la lista paginada de compras."""
        data, error = APIClient.get('/compras/', params={"page": page, "per_page": per_page})
        if error:
            print(f"Error al obtener compras: {error}")
            return {"items": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}
        if isinstance(data, dict) and "items" in data:
            return data
        if isinstance(data, list):
            return {"items": data, "total": len(data), "page": 1, "per_page": len(data), "total_pages": 1}
        return {"items": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}

    @staticmethod
    def obtener_por_id(compra_id):
        """Obtiene los detalles de una compra específica por su ID."""
        data, error = APIClient.get(f'/compras/{compra_id}')
        if error:
            print(f"Error al obtener compra {compra_id}: {error}")
            return None
        return data

    @staticmethod
    def crear(datos_compra):
        """Registra una nueva compra enviando los datos JSON al backend."""
        return APIClient.post('/compras/', data=datos_compra)

    @staticmethod
    def actualizar(compra_id, datos_compra):
        """Actualiza una compra existente."""
        return APIClient.put(f'/compras/{compra_id}', data=datos_compra)

    @staticmethod
    def eliminar(compra_id):
        """Elimina una compra por su ID."""
        return APIClient.delete(f'/compras/{compra_id}')
