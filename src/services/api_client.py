import requests
from flask import current_app, session, flash, redirect, url_for

class APIClient:
    """
    Cliente base HTTP para comunicarse con el Backend (PYMES_BE).
    Maneja las peticiones GET, POST, PUT, DELETE, construye las URLs con API_BASE_URL,
    adjunta tokens JWT de autenticación y gestiona automáticamente el cierre de sesión si el token expira.
    """

    @classmethod
    def _get_base_url(cls):
        """Obtiene la URL base desde la configuración activa de Flask."""
        base_url = current_app.config.get('API_BASE_URL', 'http://127.0.0.1:5000/api')
        return base_url.rstrip('/')

    @classmethod
    def _get_headers(cls):
        """Obtiene encabezados HTTP con Token JWT de la sesión si está disponible."""
        headers = {}
        token = session.get("access_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        empresa_activa = session.get("empresa_activa", {})
        empresa_id = empresa_activa.get("id") if isinstance(empresa_activa, dict) else session.get("empresa_id")
        if empresa_id:
            headers["X-Empresa-ID"] = str(empresa_id)
        return headers

    @classmethod
    def _check_token_expired(cls, response):
        """
        Si el backend responde con 401/422 indicando token caducado, 
        limpia la sesión automáticamente y avisa al usuario para que vuelva a iniciar sesión.
        """
        if response is not None and response.status_code in (401, 422):
            if session.get("access_token") or session.get("usuario"):
                session.clear()
                flash("Tu sesión ha expirado por seguridad. Por favor inicia sesión nuevamente para renovar tu token de acceso.", "warning")

    @classmethod
    def _parse_error(cls, response, exception):
        """Extrae el mensaje de error de la respuesta del Backend si está presente."""
        cls._check_token_expired(response)
        try:
            if response is not None:
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
        headers = cls._get_headers()
        try:
            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code in (401, 422) and "Authorization" in headers:
                cls._check_token_expired(response)
                headers_no_auth = {k: v for k, v in headers.items() if k != "Authorization"}
                response = requests.get(url, params=params, headers=headers_no_auth, timeout=5)
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            err_msg = cls._parse_error(getattr(e, 'response', None), e)
            return None, err_msg

    @classmethod
    def post(cls, endpoint, data=None):
        """Realiza una petición POST enviando datos JSON al backend."""
        url = f"{cls._get_base_url()}{endpoint}"
        headers = cls._get_headers()
        try:
            response = requests.post(url, json=data, headers=headers, timeout=5)
            if response.status_code in (401, 422) and "Authorization" in headers:
                cls._check_token_expired(response)
                headers_no_auth = {k: v for k, v in headers.items() if k != "Authorization"}
                response = requests.post(url, json=data, headers=headers_no_auth, timeout=5)
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            err_msg = cls._parse_error(getattr(e, 'response', None), e)
            return None, err_msg

    @classmethod
    def put(cls, endpoint, data=None):
        """Realiza una petición PUT para actualizar datos en el backend."""
        url = f"{cls._get_base_url()}{endpoint}"
        headers = cls._get_headers()
        try:
            response = requests.put(url, json=data, headers=headers, timeout=5)
            if response.status_code in (401, 422) and "Authorization" in headers:
                cls._check_token_expired(response)
                headers_no_auth = {k: v for k, v in headers.items() if k != "Authorization"}
                response = requests.put(url, json=data, headers=headers_no_auth, timeout=5)
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
            response = requests.delete(url, headers=cls._get_headers(), timeout=5)
            if response.status_code in (401, 422):
                cls._check_token_expired(response)
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            err_msg = cls._parse_error(getattr(e, 'response', None), e)
            return None, err_msg
