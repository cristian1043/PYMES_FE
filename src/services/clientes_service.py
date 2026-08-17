from src.services.api_client import APIClient

class ClientesService:
    """
    Servicio para consumir la API de clientes del Backend.
    """

    @staticmethod
    def obtener_todos(page=1, per_page=10):
        """Obtiene la lista paginada de clientes."""
        data, error = APIClient.get('/clientes/', params={"page": page, "per_page": per_page})
        if error:
            print(f"Error al obtener clientes: {error}")
            return {"items": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}
        if isinstance(data, dict) and "items" in data:
            return data
        if isinstance(data, list):
            return {"items": data, "total": len(data), "page": 1, "per_page": len(data), "total_pages": 1}
        return {"items": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}

    @staticmethod
    def obtener_por_id(cliente_id):
        """Obtiene un cliente por su ID."""
        data, error = APIClient.get(f'/clientes/{cliente_id}')
        if error:
            print(f"Error al obtener cliente {cliente_id}: {error}")
            return None
        return data

    @staticmethod
    def crear(datos_cliente):
        """Crea un nuevo cliente enviando datos JSON."""
        return APIClient.post('/clientes/', data=datos_cliente)

    @staticmethod
    def actualizar(cliente_id, datos_cliente):
        """Actualiza la información de un cliente existente."""
        return APIClient.put(f'/clientes/{cliente_id}', data=datos_cliente)

    @staticmethod
    def eliminar(cliente_id):
        """Elimina un cliente por su ID."""
        return APIClient.delete(f'/clientes/{cliente_id}')
