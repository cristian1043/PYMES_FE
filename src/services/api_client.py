import requests
from flask import current_app

class APIClient:
    """
    Cliente base HTTP para comunicarse con el Backend (PYMES_BE).
    Maneja las peticiones GET, POST, PUT, DELETE, construye las URLs con API_BASE_URL
    y gestiona errores de conexión.
    """

    @classmethod
    def _get_base_url(cls):
        """Obtiene la URL base desde la configuración activa de Flask."""
        return current_app.config.get('API_BASE_URL', 'http://127.0.0.1:5000/api')

    @classmethod
    def _parse_error(cls, response, exception):
        """Extrae el mensaje de error de la respuesta del Backend si está presente."""
        try:
            json_resp = response.json()
            if isinstance(json_resp, dict) and 'mensaje' in json_resp:
                return json_resp['mensaje']
        except Exception:
            pass
        return str(exception)

    @classmethod
    def get(cls, endpoint, params=None):
        """Realiza una petición GET al backend."""
        url = f"{cls._get_base_url()}{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            err_msg = cls._parse_error(getattr(e, 'response', None), e)
            return None, err_msg

    @classmethod
    def post(cls, endpoint, data=None):
        """Realiza una petición POST enviando datos JSON al backend."""
        url = f"{cls._get_base_url()}{endpoint}"
        try:
            response = requests.post(url, json=data, timeout=5)
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            err_msg = cls._parse_error(getattr(e, 'response', None), e)
            return None, err_msg

    @classmethod
    def put(cls, endpoint, data=None):
        """Realiza una petición PUT para actualizar datos en el backend."""
        url = f"{cls._get_base_url()}{endpoint}"
        try:
            response = requests.put(url, json=data, timeout=5)
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            err_msg = cls._parse_error(getattr(e, 'response', None), e)
            return None, err_msg

    @classmethod
    def delete(cls, endpoint):
        """Realiza una petición DELETE para eliminar un recurso en el backend."""
        url = f"{cls._get_base_url()}{endpoint}"
        try:
            response = requests.delete(url, timeout=5)
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            err_msg = cls._parse_error(getattr(e, 'response', None), e)
            return None, err_msg
