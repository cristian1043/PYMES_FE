from flask import session
from src.services.api_client import APIClient


class EmpresasService:
    """
    Servicio para consumir la API de empresas y membresías del Backend (PYMES_BE).
    Sin creación automática de empresas ficticias; respeta estrictamente las empresas autorizadas.
    """

    @staticmethod
    def obtener_todas(filtrar_por_usuario=True):
        """
        Obtiene la lista de empresas autorizadas desde el backend.
        - Respeta estrictamente las empresas vinculadas al usuario autenticado.
        - Solo un Super Administrador global (`es_super_admin=True`) omite el filtro local.
        """
        data, error = APIClient.get("/empresas/")
        if error or not data:
            return []

        todas = data.get("items", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        if not filtrar_por_usuario:
            return todas

        usuario = session.get("usuario", {})
        if usuario.get("es_super_admin") is True:
            return todas

        empresas_ids = usuario.get("empresas", [])
        if isinstance(empresas_ids, list) and empresas_ids:
            ids_permitidos = {str(eid) for eid in empresas_ids}
            return [e for e in todas if isinstance(e, dict) and str(e.get("id")) in ids_permitidos]

        return todas

    @staticmethod
    def obtener_por_id(id):
        data, error = APIClient.get(f"/empresas/{id}")
        if error:
            return None
        return data

    @staticmethod
    def crear(data):
        return APIClient.post("/empresas/", data=data)

    @staticmethod
    def actualizar(id, data):
        return APIClient.put(f"/empresas/{id}", data=data)

    @staticmethod
    def obtener_membresia(empresa_id):
        data, error = APIClient.get(f"/membresias/empresa/{empresa_id}")
        if error or not isinstance(data, dict):
            return {"membresia": {}, "cobro_pendiente": None, "historial_pagos": []}
        return data

    @staticmethod
    def obtener_estado_membresia(empresa_id):
        return EmpresasService.obtener_membresia(empresa_id)

    @staticmethod
    def iniciar_cobro_membresia(empresa_id, data):
        return APIClient.post(f"/membresias/empresa/{empresa_id}/cobrar", data=data)

    @staticmethod
    def consultar_cobro_membresia(cobro_id):
        return APIClient.get(f"/membresias/cobros/{cobro_id}")

    @staticmethod
    def simular_cobro_membresia(cobro_id, resultado="APROBADA"):
        return APIClient.post(f"/membresias/cobros/{cobro_id}/simular", data={"resultado": resultado})

    @staticmethod
    def cancelar_cobro_membresia(cobro_id):
        return APIClient.post(f"/membresias/cobros/{cobro_id}/cancelar", data={})
