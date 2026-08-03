from flask import Flask, render_template, request, redirect, url_for, session

def create_app(config_name='default'):
    app = Flask(__name__)
    
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
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(compras_bp)
    app.register_blueprint(facturas_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(empresas_bp)
    
    # Middleware para proteger todas las rutas privadas de la aplicación
    @app.before_request
    def proteger_rutas():
        # Permitir libre acceso a login, registro, selector de empresas y archivos estáticos
        rutas_publicas = ['auth.login', 'auth.register', 'auth.seleccionar_empresa', 'auth.activar_empresa', 'auth.logout', 'static']
        
        if request.endpoint and request.endpoint not in rutas_publicas:
            if 'usuario' not in session:
                return redirect(url_for('auth.login'))
            
            if 'empresa_activa' not in session:
                return redirect(url_for('auth.seleccionar_empresa'))

    @app.route('/')
    def index():
        return render_template('index.html')
        
    return app