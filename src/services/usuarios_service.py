from src.services.api_client import APIClient

class UsuariosService:
    """
    Servicio para gestionar la lista de usuarios, asignación de roles y estados desde el Backend.
    """

    @staticmethod
    def obtener_todos():
        """Obtiene la lista completa de usuarios registrados."""
        data, error = APIClient.get('/usuarios/')
        if error:
            print(f"Error al obtener usuarios: {error}")
            return []
        return data if data is not None else []

    @staticmethod
    def obtener_por_id(usuario_id):
        """Obtiene un usuario por su ID."""
        data, error = APIClient.get(f'/usuarios/{usuario_id}')
        if error:
            print(f"Error al obtener usuario {usuario_id}: {error}")
            return None
        return data

    @staticmethod
    def cambiar_rol(usuario_id, nuevo_rol_id):
        """Actualiza el rol_id de un usuario específico en el Backend."""
        usuario = UsuariosService.obtener_por_id(usuario_id)
        if not usuario:
            return None, "Usuario no encontrado"

        usuario['id_rol'] = int(nuevo_rol_id)
        return APIClient.put(f'/usuarios/{usuario_id}', data=usuario)

    @staticmethod
    def cambiar_estado(usuario_id, nuevo_estado):
        """Actualiza el estado laboral (Activo / Desvinculado) de un usuario en el Backend."""
        usuario = UsuariosService.obtener_por_id(usuario_id)
        if not usuario:
            return None, "Usuario no encontrado"

        usuario['estado'] = nuevo_estado
        return APIClient.put(f'/usuarios/{usuario_id}', data=usuario)

    @staticmethod
    def obtener_roles():
        """Obtiene la lista de roles registrados en el sistema."""
        data, error = APIClient.get('/roles/')
        if error or not data:
            return [
                {'id': 1, 'nombre': 'Administrador'},
                {'id': 2, 'nombre': 'Vendedor'},
                {'id': 3, 'nombre': 'Almacenista'}
            ]
        return data
