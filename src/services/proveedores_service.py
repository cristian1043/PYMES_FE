from src.services.api_client import APIClient

class ProveedoresService:
    """
    Servicio para consumir la API de proveedores del Backend.
    """

    @staticmethod
    def obtener_todos():
        """Obtiene la lista completa de proveedores."""
        data, error = APIClient.get('/proveedores/')
        if error:
            print(f"Error al obtener proveedores: {error}")
            return []
        return data if data is not None else []

    @staticmethod
    def obtener_por_id(proveedor_id):
        """Obtiene un proveedor por su ID."""
        data, error = APIClient.get(f'/proveedores/{proveedor_id}')
        if error:
            print(f"Error al obtener proveedor {proveedor_id}: {error}")
            return None
        return data

    @staticmethod
    def crear(datos_proveedor):
        """Crea un nuevo proveedor."""
        return APIClient.post('/proveedores/', data=datos_proveedor)

    @staticmethod
    def actualizar(proveedor_id, datos_proveedor):
        """Actualiza un proveedor existente."""
        return APIClient.put(f'/proveedores/{proveedor_id}', data=datos_proveedor)

    @staticmethod
    def eliminar(proveedor_id):
        """Elimina un proveedor por su ID."""
        return APIClient.delete(f'/proveedores/{proveedor_id}')
