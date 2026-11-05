from flask import session
from src.services.api_client import APIClient

class FacturasService:
    """
    Servicio para consumir la API de facturación, terminales y pasarelas de pago del Backend.
    """

    @staticmethod
    def _empresa_activa_id():
        emp = session.get("empresa_activa")
        if isinstance(emp, dict) and emp.get("id"):
            return emp.get("id")
        return session.get("empresa_id") or 1

    @staticmethod
    def obtener_todas(page=1, per_page=10):
        """Obtiene la lista paginada de facturas."""
        emp_id = FacturasService._empresa_activa_id()
        data, error = APIClient.get('/facturas/', params={"page": page, "per_page": per_page, "empresa_id": emp_id})
        if error:
            print(f"Error al obtener facturas: {error}")
            return {"items": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}
        if isinstance(data, dict) and "items" in data:
            return data
        if isinstance(data, list):
            return {"items": data, "total": len(data), "page": 1, "per_page": len(data), "total_pages": 1}
        return {"items": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}

    @staticmethod
    def obtener_por_id(factura_id):
        """Obtiene los detalles de una factura específica por su ID."""
        data, error = APIClient.get(f'/facturas/{factura_id}')
        if error:
            print(f"Error al obtener factura {factura_id}: {error}")
            return None
        return data

    @staticmethod
    def crear(datos_factura):
        """Crea una nueva factura de venta."""
        if isinstance(datos_factura, dict) and not datos_factura.get("id_empresa"):
            datos_factura["id_empresa"] = FacturasService._empresa_activa_id()
        return APIClient.post('/facturas/', data=datos_factura)

    @staticmethod
    def actualizar(factura_id, datos_factura):
        """Actualiza una factura existente."""
        return APIClient.put(f'/facturas/{factura_id}', data=datos_factura)

    @staticmethod
    def obtener_siguiente_numero():
        """Obtiene el número consecutivo automático recomendado para la nueva factura."""
        emp_id = FacturasService._empresa_activa_id()
        data, error = APIClient.get('/facturas/siguiente_numero', params={"empresa_id": emp_id})
        if error or not data:
            return "FAC-001"
        return data.get("siguiente_numero", "FAC-001")

    @staticmethod
    def eliminar(factura_id):
        """Elimina una factura por su ID."""
        return APIClient.delete(f'/facturas/{factura_id}')

    @staticmethod
    def cancelar(factura_id):
        """Cancela una factura emitida."""
        return APIClient.post(f'/facturas/{factura_id}/cancelar')

    @staticmethod
    def obtener_metodos_pago():
        """Obtiene la lista de métodos de pago disponibles (Efectivo, Tarjeta, Transferencia, Bold, Wompi...)."""
        emp_id = FacturasService._empresa_activa_id()
        data, error = APIClient.get('/metodos_pago/', params={"empresa_id": emp_id})
        if error:
            print(f"Error al obtener métodos de pago: {error}")
            return []
        return data if isinstance(data, list) else []

    @staticmethod
    def obtener_terminales(solo_activas=True):
        """Obtiene las terminales de pago (datáfonos Bold / Simulado) de la empresa activa."""
        emp_id = FacturasService._empresa_activa_id()
        params = {"empresa_id": emp_id}
        if solo_activas:
            params["solo_activas"] = "1"
        data, error = APIClient.get('/terminales/', params=params)
        if error or not isinstance(data, list):
            return []
        return data

    @staticmethod
    def obtener_cobros(factura_id):
        """Lista los intentos/transacciones de cobro asociados a una factura."""
        data, error = APIClient.get(f'/facturas/{factura_id}/cobros')
        if error or not isinstance(data, list):
            return []
        return data

    @staticmethod
    def crear_cobro(factura_id, payload):
        """Inicia un cobro en terminal (datáfono Bold) o link de pago (Wompi / Simulado)."""
        return APIClient.post(f'/facturas/{factura_id}/cobros', data=payload)

    @staticmethod
    def pagar_manual(factura_id, payload):
        """Registra un pago manual (efectivo / transferencia directa sin pasarela)."""
        return APIClient.post(f'/facturas/{factura_id}/pagar', data=payload)

    @staticmethod
    def simular_cobro(cobro_id, resultado="APPROVED"):
        """Resuelve un cobro en modo pruebas (Simulado / Sandbox) como APPROVED o DECLINED."""
        return APIClient.post(f'/cobros/{cobro_id}/simular', data={"resultado": resultado})

    @staticmethod
    def consultar_cobro(cobro_id):
        """Consulta y sincroniza el estado de un cobro con la pasarela."""
        return APIClient.get(f'/cobros/{cobro_id}')
