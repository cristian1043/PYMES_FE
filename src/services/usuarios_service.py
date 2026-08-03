from src.services.api_client import APIClient

class UsuariosService:
    """
    Servicio para consumir la API de usuarios y vinculaciones multitenant del Backend en MySQL.
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
    def obtener_estado_en_empresa(usuario_id, empresa_id):
        """Obtiene el estado laboral independiente de la BD MySQL del Backend (/api/usuario_empresas/estado)."""
        data, error = APIClient.get(f'/usuario_empresas/estado?usuario_id={usuario_id}&empresa_id={empresa_id}')
        if error or not data:
            return 'Activo'
        return data.get('estado', 'Activo')

    @staticmethod
    def cambiar_estado_en_empresa(usuario_id, empresa_id, nuevo_estado):
        """Persiste el nuevo estado laboral en la tabla MySQL del Backend (/api/usuario_empresas/estado)."""
        payload = {
            "usuario_id": int(usuario_id),
            "empresa_id": int(empresa_id),
            "estado": nuevo_estado
        }
        return APIClient.put('/usuario_empresas/estado', data=payload)

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
