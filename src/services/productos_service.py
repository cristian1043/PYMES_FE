from src.services.api_client import APIClient

class ProductosService:
    """
    Servicio para consumir la API de productos y categorías del Backend.
    """

    @staticmethod
    def obtener_todos(page=1, per_page=10):
        """Obtiene la lista paginada de productos o lista vacía."""
        data, error = APIClient.get('/productos/', params={"page": page, "per_page": per_page})
        if error:
            print(f"Error al obtener productos: {error}")
            return {"items": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}
        if isinstance(data, dict) and "items" in data:
            return data
        if isinstance(data, list):
            return {"items": data, "total": len(data), "page": 1, "per_page": len(data), "total_pages": 1}
        return {"items": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}

    @staticmethod
    def obtener_por_id(producto_id):
        """Obtiene un producto por su ID."""
        data, error = APIClient.get(f'/productos/{producto_id}')
        if error:
            print(f"Error al obtener producto {producto_id}: {error}")
            return None
        return data

    @staticmethod
    def crear(datos_producto):
        """Crea un nuevo producto."""
        return APIClient.post('/productos/', data=datos_producto)

    @staticmethod
    def actualizar(producto_id, datos_producto):
        """Actualiza un producto existente."""
        return APIClient.put(f'/productos/{producto_id}', data=datos_producto)

    @staticmethod
    def eliminar(producto_id):
        """Elimina un producto por su ID."""
        return APIClient.delete(f'/productos/{producto_id}')

    @staticmethod
    def obtener_categorias():
        """Obtiene las categorías disponibles para asignar a productos."""
        data, error = APIClient.get('/categorias/')
        if error:
            print(f"Error al obtener categorías: {error}")
            return []
        return data if data is not None else []
