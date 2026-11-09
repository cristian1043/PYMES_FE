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
            usuario = resp.get("usuario", {})
            if "rol_id" not in usuario and "id_rol" in usuario:
                usuario["rol_id"] = usuario.get("id_rol")
            session["usuario"] = usuario
            return usuario, None

        return None, "Error inesperado al iniciar sesión"

    @staticmethod
    def logout():
        """Limpia los tokens y datos del usuario de la sesión."""
        session.clear()

    @staticmethod
    def logout_global():
        """Invalida el token_version en el backend y limpia la sesión."""
        if session.get("access_token"):
            APIClient.post('/auth/logout-global', data={})
        session.clear()

    @staticmethod
    def registrar(datos_usuario):
        """
        Envía la solicitud de creación de un nuevo usuario a la API del Backend (/api/usuarios/).
        """
        return APIClient.post('/usuarios/', data=datos_usuario)

    @staticmethod
    def cambiar_password(usuario_id, password_actual, password_nueva):
        """
        Solicita al backend cambiar la contraseña validando la clave actual.
        """
        return APIClient.post('/auth/cambiar-password', data={
            "usuario_id": usuario_id,
            "password_actual": password_actual,
            "password_nueva": password_nueva
        })

    @staticmethod
    def solicitar_recuperacion(identificador):
        """
        Solicita al backend generar el token y código OTP para recuperar contraseña.
        """
        return APIClient.post('/auth/recuperar-password-solicitar', data={
            "identificador": identificador
        })

    @staticmethod
    def confirmar_recuperacion(token_o_codigo, password_nueva, identificador=None):
        """
        Envía al backend el token o código OTP con la nueva contraseña.
        """
        payload = {
            "token": token_o_codigo,
            "password_nueva": password_nueva
        }
        if identificador:
            payload["identificador"] = identificador
        return APIClient.post('/auth/recuperar-password-confirmar', data=payload)

    @staticmethod
    def solicitar_eliminacion_cuenta(password_actual):
        """
        Paso 1 de verificación en 2 pasos para eliminar la cuenta del usuario activo.
        """
        return APIClient.post('/auth/eliminar-cuenta-solicitar', data={
            "password_actual": password_actual
        })

    @staticmethod
    def confirmar_eliminacion_cuenta(codigo):
        """
        Paso 2 de verificación en 2 pasos: confirma el código OTP de 6 dígitos y elimina la cuenta.
        """
        return APIClient.post('/auth/eliminar-cuenta-confirmar', data={
            "codigo": codigo
        })
