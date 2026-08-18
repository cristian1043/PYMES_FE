from flask import session
from src.services.api_client import APIClient

class AuthService:
    """
    Servicio de autenticación para validar e inscribir usuarios utilizando JWT contra el Backend.
    """

    @staticmethod
    def autenticar(identificador, password):
        """
        Valida credenciales contra /api/auth/login, guarda el JWT en la sesión y retorna el usuario.
        """
        resp, error = APIClient.post('/auth/login', data={
            "email": identificador,
            "password": password
        })

        if error:
            return None, error

        if resp and resp.get("exito"):
            session.clear()
            session["access_token"] = resp.get("access_token")
            session["refresh_token"] = resp.get("refresh_token")
            session["usuario"] = resp.get("usuario")
            return resp.get("usuario"), None

        return None, "Error inesperado al iniciar sesión"

    @staticmethod
    def logout():
        """Limpia los tokens y datos del usuario de la sesión."""
        session.pop("access_token", None)
        session.pop("refresh_token", None)
        session.pop("usuario", None)
        session.pop("empresa_id", None)

    @staticmethod
    def registrar(datos_usuario):
        """
        Envía la solicitud de creación de un nuevo usuario a la API del Backend (/api/usuarios/).
        """
        return APIClient.post('/usuarios/', data=datos_usuario)
