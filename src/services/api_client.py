import requests
from flask import current_app, session, flash, redirect, url_for

class APIClient:
    """
    Cliente base HTTP para comunicarse con el Backend (PYMES_BE).
    Maneja las peticiones GET, POST, PUT, DELETE, construye las URLs con API_BASE_URL,
    adjunta tokens JWT de autenticación y refresca tokens de acceso automáticamente si expiran.
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
    def _try_refresh_token(cls):
        """Intenta renovar el access_token expirado usando el refresh_token almacenado en la sesión."""
        refresh_token = session.get("refresh_token")
        if not refresh_token:
            return False
        url = f"{cls._get_base_url()}/auth/refresh"
        headers = {"Authorization": f"Bearer {refresh_token}"}
        try:
            res = requests.post(url, headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                new_token = data.get("access_token")
                if new_token:
                    session["access_token"] = new_token
                    return True
        except Exception as e:
            print(f"Error al refrescar token: {str(e)}")
        return False

    @classmethod
    def _check_token_expired(cls, response):
        """
        Si el backend responde con 401/422 y no se pudo renovar el token,
        limpia la sesión automáticamente y avisa al usuario.
        """
        if response is not None and response.status_code in (401, 422):
            if session.get("access_token") or session.get("usuario"):
                session.clear()
                flash("Tu sesión ha expirado por seguridad. Por favor inicia sesión nuevamente.", "warning")

    @classmethod
    def _parse_error(cls, response, exception):
        """Extrae el mensaje de error de la respuesta del Backend si está presente."""
        try:
            if response is not None:
                json_resp = response.json()
                if isinstance(json_resp, dict):
                    if 'mensaje' in json_resp:
                        return json_resp['mensaje']
                    if 'msg' in json_resp:
                        return json_resp['msg']
                    if 'error' in json_resp:
                        return json_resp['error']
        except Exception:
            pass
        return str(exception)

    @classmethod
    def get(cls, endpoint, params=None):
        """Realiza una petición GET al backend con auto-refresh de token."""
        url = f"{cls._get_base_url()}{endpoint}"
        headers = cls._get_headers()
        try:
            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code == 401 and endpoint not in ("/auth/login", "/auth/refresh"):
                if cls._try_refresh_token():
                    headers = cls._get_headers()
                    response = requests.get(url, params=params, headers=headers, timeout=5)
                else:
                    cls._check_token_expired(response)
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            err_msg = cls._parse_error(getattr(e, 'response', None), e)
            return None, err_msg

    @classmethod
    def post(cls, endpoint, data=None):
        """Realiza una petición POST enviando datos JSON al backend con auto-refresh de token."""
        url = f"{cls._get_base_url()}{endpoint}"
        headers = cls._get_headers()
        try:
            response = requests.post(url, json=data, headers=headers, timeout=5)
            if response.status_code == 401 and endpoint not in ("/auth/login", "/auth/refresh"):
                if cls._try_refresh_token():
                    headers = cls._get_headers()
                    response = requests.post(url, json=data, headers=headers, timeout=5)
                else:
                    cls._check_token_expired(response)
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            err_msg = cls._parse_error(getattr(e, 'response', None), e)
            return None, err_msg

    @classmethod
    def put(cls, endpoint, data=None):
        """Realiza una petición PUT para actualizar datos en el backend con auto-refresh de token."""
        url = f"{cls._get_base_url()}{endpoint}"
        headers = cls._get_headers()
        try:
            response = requests.put(url, json=data, headers=headers, timeout=5)
            if response.status_code == 401 and endpoint not in ("/auth/login", "/auth/refresh"):
                if cls._try_refresh_token():
                    headers = cls._get_headers()
                    response = requests.put(url, json=data, headers=headers, timeout=5)
                else:
                    cls._check_token_expired(response)
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            err_msg = cls._parse_error(getattr(e, 'response', None), e)
            return None, err_msg

    @classmethod
    def delete(cls, endpoint):
        """Realiza una petición DELETE para eliminar un recurso en el backend con auto-refresh de token."""
        url = f"{cls._get_base_url()}{endpoint}"
        headers = cls._get_headers()
        try:
            response = requests.delete(url, headers=headers, timeout=5)
            if response.status_code == 401 and endpoint not in ("/auth/login", "/auth/refresh"):
                if cls._try_refresh_token():
                    headers = cls._get_headers()
                    response = requests.delete(url, headers=headers, timeout=5)
                else:
                    cls._check_token_expired(response)
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            err_msg = cls._parse_error(getattr(e, 'response', None), e)
            return None, err_msg
