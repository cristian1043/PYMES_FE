from src.services.api_client import APIClient

class AuthService:
    """
    Servicio de autenticación para validar e inscribir nuevos usuarios contra el Backend.
    """

    @staticmethod
    def autenticar(identificador, password):
        """
        Valida las credenciales globales del usuario (correo o documento) permitiendo el inicio de sesión.
        El acceso a cada empresa específica se valida a nivel de espacio de trabajo.
        """
        usuarios, error = APIClient.get('/usuarios/')
        if error:
            return None, "No se pudo conectar con el servidor de autenticación."

        if not usuarios:
            return None, "No existen usuarios registrados en la base de datos."

        identificador_clean = str(identificador).strip().lower()

        for user in usuarios:
            user_email = str(user.get('email', '')).strip().lower()
            user_doc = str(user.get('documento', '')).strip().lower()

            if identificador_clean == user_email or identificador_clean == user_doc:
                pass_hash = str(user.get('password_hash', ''))
                if pass_hash == password or pass_hash == password.strip():
                    return user, None
                else:
                    return None, "La contraseña ingresada es incorrecta."

        return None, "El usuario o correo electrónico no se encuentra registrado."

    @staticmethod
    def registrar(datos_usuario):
        """
        Envía la solicitud de creación de un nuevo usuario a la API del Backend (/api/usuarios/).
        """
        return APIClient.post('/usuarios/', data=datos_usuario)
