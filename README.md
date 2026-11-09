# PYMES_FE - Aplicación Web Administrativa (PYMESOFT)

Aplicación web administrativa del ecosistema **PYMESOFT**, construida con **Python 3**, **Flask 3** (Application Factory + Blueprints), **Jinja2**, **Requests** y **Bootstrap 4**, operando como cliente desacoplado de la API REST de `PYMES_BE`.

---

## 🏗️ Arquitectura del Proyecto

```text
PYMES_FE/
├── requirements.txt                # Dependencias (Flask, requests, python-dotenv, gunicorn)
└── src/
    ├── app.py                      # Punto de arranque del servidor Web (Puerto 5001)
    ├── __init__.py                 # Factory create_app(), cargador dinámico de plantillas y middleware de sesión/empresa
    ├── config/
    │   └── config.py               # Variables de entorno, SECRET_KEY y API_BASE_URL
    ├── routes/                     # Capa de presentación y enrutamiento (Flask Blueprints)
    │   ├── auth_routes.py          # Autenticación, registro, recuperación de contraseña y cambio de espacio de trabajo
    │   ├── empresas_routes.py      # Configuración fiscal, estado operativo y membresía empresarial ($19.900 COP/mes)
    │   ├── facturas_routes.py      # Facturación, cobros con datáfono Bold / link Wompi y simulador Sandbox
    │   ├── terminales_routes.py    # Administración de datáfonos y pasarelas de pago
    │   ├── compras_routes.py       # Registro e historial de compras a proveedores
    │   ├── productos_routes.py     # Catálogo de productos y control de stock
    │   ├── clientes_routes.py      # Directorio de clientes
    │   ├── proveedores_routes.py   # Directorio de proveedores
    │   ├── reportes_routes.py      # Reportes de ventas, clientes e inventario
    │   └── usuarios_routes.py      # Gestión de usuarios por empresa y perfil personal
    ├── services/                   # Capa de servicios e integración REST
    │   ├── api_client.py           # Cliente HTTP centralizado (Bearer JWT, refresh automático y header X-Empresa-ID)
    │   └── *_service.py            # Servicios por módulo que encapsulan las llamadas a PYMES_BE
    ├── templates/                  # Plantillas HTML renderizadas con Jinja2 y Bootstrap 4
    └── utils/
        └── decorators.py           # Decorador @requiere_rol para autorización por rol en la empresa activa
```

---

## ▶️ Ejecución Local

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Asegurarse de que `PYMES_BE` esté ejecutándose en `http://127.0.0.1:5000`.
3. Iniciar la aplicación web en el puerto `5001`:
   ```bash
   python src/app.py
   ```
