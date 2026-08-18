from src.services.api_client import APIClient

class UsuariosService:
    """
    Servicio para consumir la API de usuarios y vinculaciones multitenant (Rol + Estado independiente por empresa) del Backend en MySQL.
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
    def actualizar(usuario_id, datos_usuario):
        """Actualiza los datos personales, de contacto y bancarios de un usuario."""
        return APIClient.put(f'/usuarios/{usuario_id}', data=datos_usuario)

    @staticmethod
    def obtener_vinculacion_empresa(usuario_id, empresa_id):
        """Obtiene el rol_id y estado exclusivo del usuario para una empresa en la BD MySQL."""
        if not usuario_id or not empresa_id:
            return {"rol_id": 2, "estado": "Activo"}
        data, error = APIClient.get(f'/usuario_empresas/vinculacion?usuario_id={usuario_id}&empresa_id={empresa_id}')
        if error or not isinstance(data, dict):
            return {"rol_id": 2, "estado": "Activo"}
        return data

    @staticmethod
    def cambiar_rol_en_empresa(usuario_id, empresa_id, nuevo_rol_id):
        """Actualiza el rol del usuario de forma 100% exclusiva para esa empresa en la BD MySQL."""
        payload = {
            "usuario_id": int(usuario_id),
            "empresa_id": int(empresa_id),
            "rol_id": int(nuevo_rol_id)
        }
        return APIClient.put('/usuario_empresas/vinculacion', data=payload)

    @staticmethod
    def cambiar_estado_en_empresa(usuario_id, empresa_id, nuevo_estado):
        """Actualiza el estado del usuario de forma 100% exclusiva para esa empresa en la BD MySQL."""
        payload = {
            "usuario_id": int(usuario_id),
            "empresa_id": int(empresa_id),
            "estado": nuevo_estado
        }
        return APIClient.put('/usuario_empresas/vinculacion', data=payload)

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
