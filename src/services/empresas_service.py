from src.services.api_client import APIClient

class EmpresasService:
    """
    Servicio para consumir la API de empresas del Backend.
    """

    @staticmethod
    def obtener_todas():
        """Obtiene la lista de empresas registradas desde la base de datos MySQL."""
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
    def crear(datos_empresa):
        """Crea y registra una nueva empresa en el Backend."""
        return APIClient.post('/empresas/', data=datos_empresa)

    @staticmethod
    def actualizar(empresa_id, datos_empresa):
        """Actualiza los datos internos (Nombre, NIT, Dirección, Teléfono, Correo) de la empresa."""
        return APIClient.put(f'/empresas/{empresa_id}', data=datos_empresa)

    @staticmethod
    def obtener_membresia(empresa_id):
        """Obtiene el estado de la membresía ($19.900 COP) e historial de pagos de la empresa."""
        data, error = APIClient.get(f'/membresias/empresa/{empresa_id}')
        if error or not isinstance(data, dict):
            return {
                "membresia": {
                    "plan": "Plan PYME Mensual",
                    "precio_cop": 19900.0,
                    "precio_formateado": "$19.900 COP",
                    "moneda": "COP",
                    "estado": "Activa",
                    "activa": True,
                    "dias_restantes": 30,
                },
                "cobro_pendiente": None,
                "historial_pagos": [],
            }
        return data

    @staticmethod
    def iniciar_cobro_membresia(empresa_id, payload):
        """Inicia un cobro de membresía de $19.900 COP en pasarela (Wompi/Simulado), datáfono (Bold) o directo."""
        datos = dict(payload or {})
        datos["id_empresa"] = empresa_id
        return APIClient.post(f'/membresias/empresa/{empresa_id}/cobrar', data=datos)

    @staticmethod
    def consultar_cobro_membresia(cobro_id):
        """Consulta y refresca el estado de una transacción de membresía."""
        return APIClient.get(f'/membresias/cobros/{cobro_id}')

    @staticmethod
    def simular_cobro_membresia(cobro_id, resultado='APROBADA'):
        """Simula la aprobación o rechazo de un cobro de membresía en modo Sandbox."""
        return APIClient.post(f'/membresias/cobros/{cobro_id}/simular', data={'resultado': resultado})

    @staticmethod
    def cancelar_cobro_membresia(cobro_id):
        """Cancela un cobro de membresía pendiente."""
        return APIClient.post(f'/membresias/cobros/{cobro_id}/cancelar', data={})
