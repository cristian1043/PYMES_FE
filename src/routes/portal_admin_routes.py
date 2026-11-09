from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from src.services.portal_admin_service import PortalAdminService
from src.services.productos_service import ProductosService
from src.services.clientes_service import ClientesService
from src.utils.decorators import requiere_rol

portal_admin_bp = Blueprint("portal_admin", __name__, url_prefix="/portal_clientes")


def _get_portal_public_url(slug):
    base = current_app.config.get("PORTAL_CLIENTES_URL", "http://127.0.0.1:5002").rstrip("/")
    return f"{base}/e/{slug}" if slug else base


@portal_admin_bp.route("/", methods=["GET", "POST"])
@requiere_rol(1, 2, 3)
def dashboard():
    """
    Panel principal del Portal de Clientes:
    - KPIs de pedidos, reservas, clientes del portal, solicitudes y notificaciones no leídas.
    - Configuración general, activación/desactivación y personalización visual (Solo Rol 1 Admin para modificar).
    """
    rol_id = int(session.get("usuario", {}).get("rol_id", 2))

    if request.method == "POST":
        if rol_id != 1:
            flash("Solo el Administrador de la empresa puede modificar la configuración general del portal.", "danger")
            return redirect(url_for("portal_admin.dashboard"))

        redes_sociales = {
            "facebook": request.form.get("facebook", "").strip(),
            "instagram": request.form.get("instagram", "").strip(),
            "tiktok": request.form.get("tiktok", "").strip(),
            "web": request.form.get("web", "").strip(),
        }
        payload = {
            "slug": request.form.get("slug", "").strip().lower(),
            "activo": request.form.get("activo") == "on",
            "nombre_publico": request.form.get("nombre_publico", "").strip(),
            "descripcion": request.form.get("descripcion", "").strip(),
            "historia": request.form.get("historia", "").strip(),
            "logo_url": request.form.get("logo_url", "").strip(),
            "banner_url": request.form.get("banner_url", "").strip(),
            "color_primario": request.form.get("color_primario", "#1e3c72").strip(),
            "color_secundario": request.form.get("color_secundario", "#2a5298").strip(),
            "telefono_publico": request.form.get("telefono_publico", "").strip(),
            "whatsapp": request.form.get("whatsapp", "").strip(),
            "correo_publico": request.form.get("correo_publico", "").strip(),
            "direccion_publica": request.form.get("direccion_publica", "").strip(),
            "horario_atencion": request.form.get("horario_atencion", "").strip(),
            "redes_sociales": redes_sociales,
            "catalogo_activo": request.form.get("catalogo_activo") == "on",
            "servicios_activos": request.form.get("servicios_activos") == "on",
            "carrito_activo": request.form.get("carrito_activo") == "on",
            "reservas_activas": request.form.get("reservas_activas") == "on",
            "mostrar_precios": request.form.get("mostrar_precios") == "on",
            "mostrar_stock": request.form.get("mostrar_stock") == "on",
            "permitir_recogida_tienda": request.form.get("permitir_recogida_tienda") == "on",
            "permitir_entrega_domicilio": request.form.get("permitir_entrega_domicilio") == "on",
            "costo_envio_base": float(request.form.get("costo_envio_base") or 0),
            "politicas_terminos": request.form.get("politicas_terminos", "").strip(),
        }
        res, err = PortalAdminService.actualizar_configuracion(payload)
        if err:
            flash(f"Error al guardar la configuración del portal: {err}", "danger")
        else:
            flash("¡Configuración del Portal de Clientes actualizada exitosamente!", "success")
            return redirect(url_for("portal_admin.dashboard"))

    config_portal, _ = PortalAdminService.obtener_configuracion()
    pedidos = PortalAdminService.listar_pedidos()
    reservas = PortalAdminService.listar_reservas()
    clientes_portal = PortalAdminService.listar_clientes_portal()
    solicitudes = PortalAdminService.listar_solicitudes()
    notificaciones = PortalAdminService.listar_notificaciones()

    no_leidas = [n for n in notificaciones if not n.get("leida")]
    pedidos_pendientes = [p for p in pedidos if p.get("estado") in ("Pendiente", "Confirmado", "En preparacion")]
    reservas_pendientes = [r for r in reservas if r.get("estado") in ("Pendiente", "Confirmada")]
    solicitudes_abiertas = [s for s in solicitudes if s.get("estado") in ("Abierta", "En revision")]

    portal_url = _get_portal_public_url(config_portal.get("slug"))

    return render_template(
        "portal_clientes/dashboard.html",
        config=config_portal,
        portal_url=portal_url,
        total_pedidos=len(pedidos),
        pedidos_pendientes=len(pedidos_pendientes),
        total_reservas=len(reservas),
        reservas_pendientes=len(reservas_pendientes),
        total_clientes=len(clientes_portal),
        solicitudes_abiertas=len(solicitudes_abiertas),
        notificaciones_no_leidas=len(no_leidas),
        ultimos_pedidos=pedidos[:5],
        ultimas_notificaciones=notificaciones[:5],
    )


@portal_admin_bp.route("/toggle_estado", methods=["POST"])
@requiere_rol(1)
def toggle_estado():
    """Activa o desactiva rápidamente el portal público de la empresa (Solo Admin)."""
    config_actual, _ = PortalAdminService.obtener_configuracion()
    nuevo_estado = not bool(config_actual.get("activo", True))
    res, err = PortalAdminService.actualizar_configuracion({"activo": nuevo_estado})
    if err:
        flash(f"No se pudo cambiar el estado del portal: {err}", "danger")
    else:
        estado_txt = "ACTIVADO (En línea)" if nuevo_estado else "PAUSADO (En mantenimiento)"
        flash(f"Portal de Clientes actualizado a: {estado_txt}", "info")
    return redirect(url_for("portal_admin.dashboard"))


@portal_admin_bp.route("/productos", methods=["GET"])
@requiere_rol(1, 3)  # Admin y Almacenista
def productos():
    """Gestión de productos publicados en el portal y consulta de inventario."""
    res_prods = ProductosService.obtener_todos(per_page=1000)
    items = res_prods.get("items", []) if isinstance(res_prods, dict) else (res_prods if isinstance(res_prods, list) else [])
    return render_template("portal_clientes/productos.html", productos=items)


@portal_admin_bp.route("/productos/<int:id_producto>/publicacion", methods=["POST"])
@requiere_rol(1, 3)
def actualizar_producto_portal(id_producto):
    """Actualiza la visibilidad, precio público, descripción pública e imagen de un producto en el portal."""
    precio_pub_raw = request.form.get("precio_publico", "").strip()
    payload = {
        "publicado_portal": request.form.get("publicado_portal") == "on",
        "disponible_portal": request.form.get("disponible_portal") == "on",
        "destacado": request.form.get("destacado") == "on",
        "precio_publico": float(precio_pub_raw) if precio_pub_raw else None,
        "descripcion_publica": request.form.get("descripcion_publica", "").strip(),
        "imagen_publica": request.form.get("imagen_publica", "").strip(),
    }
    res, err = PortalAdminService.actualizar_publicacion_producto(id_producto, payload)
    if err:
        flash(f"Error al actualizar publicación del producto: {err}", "danger")
    else:
        flash("Configuración pública del producto actualizada en el portal.", "success")
    return redirect(url_for("portal_admin.productos"))


@portal_admin_bp.route("/servicios", methods=["GET", "POST"])
@requiere_rol(1, 2)  # Admin y Vendedor
def servicios():
    """Gestión de servicios publicados en el portal."""
    rol_id = int(session.get("usuario", {}).get("rol_id", 2))
    if request.method == "POST":
        if rol_id != 1:
            flash("Solo el Administrador puede crear nuevos servicios en el catálogo.", "danger")
            return redirect(url_for("portal_admin.servicios"))

        payload = {
            "codigo": request.form.get("codigo", "").strip(),
            "nombre": request.form.get("nombre", "").strip(),
            "categoria": request.form.get("categoria", "").strip(),
            "descripcion": request.form.get("descripcion", "").strip(),
            "duracion_estimada_min": int(request.form.get("duracion_estimada_min") or 60),
            "precio": float(request.form.get("precio") or 0),
            "modalidad": request.form.get("modalidad", "Presencial"),
            "requiere_reserva": request.form.get("requiere_reserva") == "on",
            "publicado_portal": request.form.get("publicado_portal") == "on",
            "disponible": request.form.get("disponible") == "on",
            "imagen_url": request.form.get("imagen_url", "").strip(),
        }
        res, err = PortalAdminService.crear_servicio(payload)
        if err:
            flash(f"Error al crear servicio: {err}", "danger")
        else:
            flash("¡Servicio creado y publicado exitosamente!", "success")
            return redirect(url_for("portal_admin.servicios"))

    lista_servicios = PortalAdminService.listar_servicios()
    return render_template("portal_clientes/servicios.html", servicios=lista_servicios)


@portal_admin_bp.route("/servicios/<int:id_servicio>/editar", methods=["POST"])
@requiere_rol(1)
def editar_servicio(id_servicio):
    payload = {
        "nombre": request.form.get("nombre", "").strip(),
        "categoria": request.form.get("categoria", "").strip(),
        "descripcion": request.form.get("descripcion", "").strip(),
        "duracion_estimada_min": int(request.form.get("duracion_estimada_min") or 60),
        "precio": float(request.form.get("precio") or 0),
        "modalidad": request.form.get("modalidad", "Presencial"),
        "requiere_reserva": request.form.get("requiere_reserva") == "on",
        "publicado_portal": request.form.get("publicado_portal") == "on",
        "disponible": request.form.get("disponible") == "on",
        "imagen_url": request.form.get("imagen_url", "").strip(),
    }
    res, err = PortalAdminService.actualizar_servicio(id_servicio, payload)
    if err:
        flash(f"Error al actualizar servicio: {err}", "danger")
    else:
        flash("Servicio actualizado correctamente.", "success")
    return redirect(url_for("portal_admin.servicios"))


@portal_admin_bp.route("/servicios/<int:id_servicio>/eliminar", methods=["POST"])
@requiere_rol(1)
def eliminar_servicio(id_servicio):
    res, err = PortalAdminService.eliminar_servicio(id_servicio)
    if err:
        flash(f"Error al eliminar servicio: {err}", "danger")
    else:
        flash("Servicio eliminado o desactivado correctamente.", "info")
    return redirect(url_for("portal_admin.servicios"))


@portal_admin_bp.route("/pedidos", methods=["GET"])
@requiere_rol(1, 2, 3)  # Admin, Vendedor y Almacenista
def pedidos():
    """Listado de pedidos recibidos desde el Portal de Clientes."""
    estado_filtro = request.args.get("estado", "").strip()
    lista_pedidos = PortalAdminService.listar_pedidos(estado=estado_filtro or None)
    return render_template(
        "portal_clientes/pedidos.html",
        pedidos=lista_pedidos,
        estado_filtro=estado_filtro,
    )


@portal_admin_bp.route("/pedidos/<int:id_pedido>", methods=["GET"])
@requiere_rol(1, 2, 3)
def detalle_pedido(id_pedido):
    """Detalle completo de un pedido recibido, productos, cliente, dirección, historial y acciones."""
    pedido, err = PortalAdminService.obtener_pedido(id_pedido)
    if err or not pedido:
        flash(err or "Pedido no encontrado en esta empresa.", "danger")
        return redirect(url_for("portal_admin.pedidos"))
    return render_template("portal_clientes/detalle_pedido.html", pedido=pedido)


@portal_admin_bp.route("/pedidos/<int:id_pedido>/estado", methods=["POST"])
@requiere_rol(1, 2, 3)
def actualizar_estado_pedido(id_pedido):
    """Actualiza el estado del pedido respetando permisos por rol (Admin, Vendedor, Almacenista)."""
    nuevo_estado = request.form.get("estado", "").strip()
    comentario = request.form.get("comentario", "").strip()
    generar_factura = request.form.get("generar_factura") == "on"

    res, err = PortalAdminService.cambiar_estado_pedido(
        id_pedido=id_pedido,
        estado=nuevo_estado,
        comentario=comentario,
        generar_factura=generar_factura,
    )
    if err:
        flash(f"No se pudo actualizar el estado del pedido: {err}", "danger")
    else:
        flash(f"Estado del pedido actualizado a '{nuevo_estado}'.", "success")
    return redirect(url_for("portal_admin.detalle_pedido", id_pedido=id_pedido))


@portal_admin_bp.route("/reservas", methods=["GET"])
@requiere_rol(1, 2)  # Admin y Vendedor
def reservas():
    """Gestión de reservas/citas recibidas y vista de calendario/agenda por fecha."""
    estado_filtro = request.args.get("estado", "").strip()
    fecha_filtro = request.form.get("fecha") or request.args.get("fecha", "").strip()
    lista_reservas = PortalAdminService.listar_reservas(
        estado=estado_filtro or None,
        fecha=fecha_filtro or None,
    )
    return render_template(
        "portal_clientes/reservas.html",
        reservas=lista_reservas,
        estado_filtro=estado_filtro,
        fecha_filtro=fecha_filtro,
    )


@portal_admin_bp.route("/reservas/<int:id_reserva>/estado", methods=["POST"])
@requiere_rol(1, 2)
def actualizar_estado_reserva(id_reserva):
    nuevo_estado = request.form.get("estado", "").strip()
    notas_empresa = request.form.get("notas_empresa", "").strip()
    res, err = PortalAdminService.cambiar_estado_reserva(
        id_reserva=id_reserva,
        estado=nuevo_estado,
        notas_empresa=notas_empresa,
    )
    if err:
        flash(f"Error al actualizar la reserva: {err}", "danger")
    else:
        flash(f"Reserva #{id_reserva} actualizada a estado '{nuevo_estado}'.", "success")
    return redirect(url_for("portal_admin.reservas"))


@portal_admin_bp.route("/clientes", methods=["GET"])
@requiere_rol(1, 2)  # Admin y Vendedor
def clientes():
    """Clientes externos registrados en el portal y gestión de su vinculación comercial."""
    vinculaciones = PortalAdminService.listar_clientes_portal()
    clientes_comerciales_res = ClientesService.obtener_todos(per_page=1000)
    clientes_comerciales = (
        clientes_comerciales_res.get("items", [])
        if isinstance(clientes_comerciales_res, dict)
        else (clientes_comerciales_res if isinstance(clientes_comerciales_res, list) else [])
    )
    return render_template(
        "portal_clientes/clientes.html",
        vinculaciones=vinculaciones,
        clientes_comerciales=clientes_comerciales,
    )


@portal_admin_bp.route("/clientes/<int:id_vinculacion>/verificar", methods=["POST"])
@requiere_rol(1, 2)
def verificar_cliente_portal(id_vinculacion):
    accion = request.form.get("accion", "aprobar").strip()
    id_cliente = request.form.get("id_cliente", "").strip()
    res, err = PortalAdminService.verificar_vinculacion_cliente(
        id_vinculacion=id_vinculacion,
        accion=accion,
        id_cliente=int(id_cliente) if id_cliente.isdigit() else None,
    )
    if err:
        flash(f"Error al procesar vinculación del cliente: {err}", "danger")
    else:
        flash(res.get("mensaje", "Vinculación actualizada correctamente."), "success")
    return redirect(url_for("portal_admin.clientes"))


@portal_admin_bp.route("/solicitudes", methods=["GET"])
@requiere_rol(1, 2)  # Admin y Vendedor
def solicitudes():
    """Consultas, reclamos o solicitudes (PQRS) recibidas desde el portal."""
    estado_filtro = request.args.get("estado", "").strip()
    lista_solicitudes = PortalAdminService.listar_solicitudes(estado=estado_filtro or None)
    return render_template(
        "portal_clientes/solicitudes.html",
        solicitudes=lista_solicitudes,
        estado_filtro=estado_filtro,
    )


@portal_admin_bp.route("/solicitudes/<int:id_solicitud>/responder", methods=["POST"])
@requiere_rol(1, 2)
def responder_solicitud(id_solicitud):
    respuesta = request.form.get("respuesta_empresa", "").strip()
    estado = request.form.get("estado", "Respondida").strip()
    res, err = PortalAdminService.responder_solicitud(
        id_solicitud=id_solicitud,
        respuesta_empresa=respuesta,
        estado=estado,
    )
    if err:
        flash(f"Error al responder la solicitud: {err}", "danger")
    else:
        flash(f"Respuesta enviada y solicitud marcada como '{estado}'.", "success")
    return redirect(url_for("portal_admin.solicitudes"))


@portal_admin_bp.route("/notificaciones", methods=["GET"])
@requiere_rol(1, 2, 3)
def notificaciones():
    """Centro de notificaciones del Portal de Clientes."""
    lista_notificaciones = PortalAdminService.listar_notificaciones()
    return render_template("portal_clientes/notificaciones.html", notificaciones=lista_notificaciones)


@portal_admin_bp.route("/notificaciones/<int:id_notif>/leer", methods=["POST"])
@requiere_rol(1, 2, 3)
def leer_notificacion(id_notif):
    PortalAdminService.marcar_notificacion_leida(id_notif)
    return redirect(request.referrer or url_for("portal_admin.notificaciones"))
