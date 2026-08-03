from src.services.api_client import APIClient

class ClientesService:
    """
    Servicio para consumir la API de clientes del Backend.
    """

    @staticmethod
    def obtener_todos():
        """Obtiene la lista completa de clientes."""
        data, error = APIClient.get('/clientes/')
        if error:
            print(f"Error al obtener clientes: {error}")
            return []
        return data if data is not None else []

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
