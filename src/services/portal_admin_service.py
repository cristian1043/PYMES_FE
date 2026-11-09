from src.services.api_client import APIClient


class PortalAdminService:
    """
    Servicio HTTP en PYMES_FE para consumir los endpoints administrativos del Portal de Clientes
    en PYMES_BE (/api/portal/admin/...).
    """

    # 1. Configuración del Portal
    @staticmethod
    def obtener_configuracion():
        data, err = APIClient.get("/portal/admin/configuracion")
        if isinstance(data, dict) and "configuracion" in data:
            return data["configuracion"] or {}, err
        return data or {}, err

    @staticmethod
    def actualizar_configuracion(payload):
        return APIClient.put("/portal/admin/configuracion", data=payload)

    # 2. Gestión de Productos Publicados
    @staticmethod
    def actualizar_publicacion_producto(id_producto, payload):
        return APIClient.put(f"/portal/admin/productos/{id_producto}/portal", data=payload)

    # 3. Gestión de Servicios Publicados
    @staticmethod
    def listar_servicios():
        data, err = APIClient.get("/portal/admin/servicios")
        if err or not data:
            return []
        if isinstance(data, dict):
            return data.get("servicios", [])
        return data if isinstance(data, list) else []

    @staticmethod
    def crear_servicio(payload):
        return APIClient.post("/portal/admin/servicios", data=payload)

    @staticmethod
    def actualizar_servicio(id_servicio, payload):
        return APIClient.put(f"/portal/admin/servicios/{id_servicio}", data=payload)

    @staticmethod
    def eliminar_servicio(id_servicio):
        return APIClient.delete(f"/portal/admin/servicios/{id_servicio}")

    # 4. Gestión de Pedidos Recibidos
    @staticmethod
    def listar_pedidos(estado=None):
        params = {"estado": estado} if estado else None
        data, err = APIClient.get("/portal/admin/pedidos", params=params)
        if err or not data:
            return []
        if isinstance(data, dict):
            return data.get("pedidos", [])
        return data if isinstance(data, list) else []

    @staticmethod
    def obtener_pedido(id_pedido):
        data, err = APIClient.get(f"/portal/admin/pedidos/{id_pedido}")
        if isinstance(data, dict) and "pedido" in data:
            return data["pedido"], err
        return data, err

    @staticmethod
    def cambiar_estado_pedido(id_pedido, estado, comentario="", generar_factura=False):
        return APIClient.put(
            f"/portal/admin/pedidos/{id_pedido}/estado",
            data={
                "estado": estado,
                "comentario": comentario,
                "generar_factura": generar_factura,
            },
        )

    # 5. Gestión de Reservas y Agenda
    @staticmethod
    def listar_reservas(estado=None, fecha=None):
        params = {}
        if estado:
            params["estado"] = estado
        if fecha:
            params["fecha"] = fecha
        data, err = APIClient.get("/portal/admin/reservas", params=params or None)
        if err or not data:
            return []
        if isinstance(data, dict):
            return data.get("reservas", [])
        return data if isinstance(data, list) else []

    @staticmethod
    def cambiar_estado_reserva(id_reserva, estado, notas_empresa=None):
        payload = {"estado": estado}
        if notas_empresa is not None:
            payload["notas_empresa"] = notas_empresa
        return APIClient.put(f"/portal/admin/reservas/{id_reserva}", data=payload)

    # 6. Clientes Registrados desde el Portal
    @staticmethod
    def listar_clientes_portal():
        data, err = APIClient.get("/portal/admin/clientes")
        if err or not data:
            return []
        if isinstance(data, dict):
            return data.get("clientes", [])
        return data if isinstance(data, list) else []

    @staticmethod
    def verificar_vinculacion_cliente(id_vinculacion, accion, id_cliente=None):
        estado_verif = "Verificado" if accion == "aprobar" else "Rechazado"
        payload = {"accion": accion, "estado_verificacion": estado_verif}
        if id_cliente:
            payload["id_cliente"] = int(id_cliente)
        return APIClient.put(f"/portal/admin/clientes/{id_vinculacion}/verificar", data=payload)

    # 7. Consultas, Reclamos y Solicitudes (PQRS)
    @staticmethod
    def listar_solicitudes(estado=None):
        params = {"estado": estado} if estado else None
        data, err = APIClient.get("/portal/admin/solicitudes", params=params)
        if err or not data:
            return []
        if isinstance(data, dict):
            return data.get("solicitudes", [])
        return data if isinstance(data, list) else []

    @staticmethod
    def responder_solicitud(id_solicitud, respuesta_empresa, estado="Respondida"):
        return APIClient.put(
            f"/portal/admin/solicitudes/{id_solicitud}",
            data={
                "respuesta": respuesta_empresa,
                "respuesta_empresa": respuesta_empresa,
                "estado": estado,
            },
        )

    # 8. Notificaciones del Portal
    @staticmethod
    def listar_notificaciones():
        data, err = APIClient.get("/portal/admin/notificaciones")
        if err or not data:
            return []
        if isinstance(data, dict):
            return data.get("notificaciones", [])
        return data if isinstance(data, list) else []

    @staticmethod
    def marcar_notificacion_leida(id_notif):
        return APIClient.post("/portal/admin/notificaciones/leer", data={"id_notificacion": id_notif})
