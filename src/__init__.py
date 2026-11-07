import os
from jinja2 import FunctionLoader
from flask import Flask, render_template, request, redirect, url_for, session, flash

def create_app(config_name='default'):
    src_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(src_dir, 'templates')
    static_dir = os.path.join(src_dir, 'static')

    def _load_template(name):
        target = name.replace('\\', '/').lstrip('/').lower()
        for root, _, files in os.walk(src_dir):
            for f in files:
                if f.lower().endswith('.html'):
                    full_path = os.path.join(root, f)
                    rel = os.path.relpath(full_path, src_dir).replace('\\', '/').lower()
                    if rel.startswith('templates/'):
                        rel = rel[len('templates/'):]
                    if rel == target or f.lower() == target:
                        with open(full_path, 'r', encoding='utf-8') as fp:
                            return fp.read(), full_path, lambda: True
        print(f"DEBUG_TEMPLATES: No se encontro '{name}' en {src_dir}. Contenido de src_dir: {os.listdir(src_dir)}", flush=True)
        return None

    app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)
    loader = FunctionLoader(_load_template)
    app.jinja_loader = loader
    app.jinja_env.loader = loader
    
    # Carga de la configuración
    from src.config.config import config
    app.config.from_object(config[config_name])
    
    # Registro de Blueprints (Rutas)
    from src.routes.auth_routes import auth_bp
    from src.routes.clientes_routes import clientes_bp
    from src.routes.productos_routes import productos_bp
    from src.routes.proveedores_routes import proveedores_bp
    from src.routes.compras_routes import compras_bp
    from src.routes.facturas_routes import facturas_bp
    from src.routes.reportes_routes import reportes_bp
    from src.routes.usuarios_routes import usuarios_bp
    from src.routes.empresas_routes import empresas_bp
    from src.routes.terminales_routes import terminales_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(compras_bp)
    app.register_blueprint(facturas_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(empresas_bp)
    app.register_blueprint(terminales_bp)
    
    # Middleware para proteger todas las rutas privadas de la aplicación
    @app.before_request
    def proteger_rutas():
        # Rutas accesibles sin iniciar sesión
        rutas_sin_login = [
            'auth.login',
            'auth.register',
            'auth.logout',
            'auth.recuperar_password',
            'auth.recuperar_password_confirmar',
            'static'
        ]
        # Rutas accesibles tras iniciar sesión pero sin haber seleccionado empresa activa aún
        rutas_sin_empresa = ['auth.seleccionar_empresa', 'auth.activar_empresa', 'empresas.nueva_empresa']

        if request.endpoint and request.endpoint not in rutas_sin_login:
            if 'usuario' not in session:
                flash("🔒 Acceso Denegado: Debes iniciar sesión con credenciales válidas para acceder a las secciones del sistema.", "danger")
                return redirect(url_for('auth.login'))
            
            if request.endpoint not in rutas_sin_empresa:
                if 'empresa_activa' not in session:
                    return redirect(url_for('auth.seleccionar_empresa'))

                # Bloqueo inmediato para empleados si la empresa activa pasa a estar Inactiva
                if session.get('usuario', {}).get('rol_id') != 1 and session.get('empresa_activa', {}).get('estado') == 'Inactivo':
                    session.pop('empresa_activa', None)
                    flash("Las operaciones de esta empresa han sido pausadas por el Administrador.", "danger")
                    return redirect(url_for('auth.seleccionar_empresa'))

    @app.route('/')
    def index():
        if 'usuario' not in session:
            return redirect(url_for('auth.login'))

        if not session.get('empresa_activa'):
            return render_template('index.html', bajos=[], sobrestock=[], optimos=[], total_productos=0, total_ventas=0, total_facturas=0)

        from src.services.productos_service import ProductosService
        from src.services.facturas_service import FacturasService
        from src.services.proveedores_service import ProveedoresService
        
        prov_res = ProveedoresService.obtener_todos(per_page=1000)
        prov_list = prov_res.get("items", []) if isinstance(prov_res, dict) else (prov_res if isinstance(prov_res, list) else [])
        prov_map = {p.get('id'): p for p in prov_list if isinstance(p, dict)}

        prods_res = ProductosService.obtener_todos(per_page=1000)
        items = prods_res.get("items", []) if isinstance(prods_res, dict) else (prods_res if isinstance(prods_res, list) else [])
        
        for p in items:
            if isinstance(p, dict):
                p['proveedor'] = prov_map.get(p.get('id_proveedor'))

        bajos = [p for p in items if p.get('stock', 0) <= 10]
        sobrestock = [p for p in items if p.get('stock', 0) > 100]
        optimos = [p for p in items if 10 < p.get('stock', 0) <= 100]
        
        facturas_res = FacturasService.obtener_todas(per_page=1000)
        fact_list = facturas_res.get("items", []) if isinstance(facturas_res, dict) else (facturas_res if isinstance(facturas_res, list) else [])
        facturas_validas = [f for f in fact_list if f.get('estado', 'Emitida') != 'Cancelada']
        total_ventas = sum(float(f.get('total', 0.0)) for f in facturas_validas)
        
        return render_template('index.html', bajos=bajos, sobrestock=sobrestock, optimos=optimos, total_productos=len(items), total_ventas=total_ventas, total_facturas=len(facturas_validas))

    @app.errorhandler(500)
    def internal_error(error):
        import traceback
        traceback.print_exc()
        original_exception = getattr(error, 'original_exception', error)
        return f"<h3>Error interno del servidor (500)</h3><p>{str(original_exception)}</p>", 500

    return app
