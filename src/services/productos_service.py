from src.services.api_client import APIClient

class ProductosService:
    """
    Servicio para consumir la API de productos y categorías del Backend.
    """

    @staticmethod
    def obtener_todos():
        """Obtiene la lista completa de productos."""
        data, error = APIClient.get('/productos/')
        if error:
            print(f"Error al obtener productos: {error}")
            return []
        return data if data is not None else []

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
