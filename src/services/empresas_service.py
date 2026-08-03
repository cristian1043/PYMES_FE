from src.services.api_client import APIClient

class EmpresasService:
    """
    Servicio para consumir la API de empresas del Backend.
    """

    @staticmethod
    def obtener_todas():
        """Obtiene la lista de empresas registradas."""
        data, error = APIClient.get('/empresas/')
        if error:
            print(f"Error al obtener empresas: {error}")
            return []
        return data if data is not None else []

    @staticmethod
    def obtener_por_id(empresa_id):
        """Obtiene los datos de una empresa específica por su ID."""
        data, error = APIClient.get(f'/empresas/{empresa_id}')
        if error:
            print(f"Error al obtener empresa {empresa_id}: {error}")
            return None
        return data

    @staticmethod
    def actualizar(empresa_id, datos_empresa):
        """Actualiza los datos internos (Nombre, NIT, Dirección, Teléfono, Correo) de la empresa."""
        return APIClient.put(f'/empresas/{empresa_id}', data=datos_empresa)
