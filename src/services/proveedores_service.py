from src.services.api_client import APIClient

class ProveedoresService:
    """
    Servicio para consumir la API de proveedores del Backend.
    """

    @staticmethod
    def obtener_todos(page=1, per_page=10):
        """Obtiene la lista paginada de proveedores."""
        data, error = APIClient.get('/proveedores/', params={"page": page, "per_page": per_page})
        if error:
            print(f"Error al obtener proveedores: {error}")
            return {"items": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}
        if isinstance(data, dict) and "items" in data:
            return data
        if isinstance(data, list):
            return {"items": data, "total": len(data), "page": 1, "per_page": len(data), "total_pages": 1}
        return {"items": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}

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
