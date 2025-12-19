from flask import Flask, redirect, url_for
from config import Config
from models import db, Usuario # Importamos el objeto db de SQLAlchemy y la clase Usuario
from flask_login import LoginManager # Necesario para los roles de admin/operador
from blueprints.auth.auth import bp as auth_bp
from blueprints.vuelos.vuelos import bp as vuelos_bp
from blueprints.aviones.aviones import bp as aviones_bp
from blueprints.tripulacion.tripulacion import bp as tripulacion_bp

# --- 1. Inicialización de la Aplicación y Extensiones ---

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar SQLAlchemy (ORM)
    db.init_app(app) # <-- CRUCIAL: Conecta la DB
    
    # Inicializar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # --- 2. Registro de Blueprints (Modularización) ---
    
    from blueprints.auth.auth import bp as auth_bp
    from blueprints.vuelos.vuelos import bp as vuelos_bp         
    from blueprints.aviones.aviones import bp as aviones_bp     
    from blueprints.tripulacion.tripulacion import bp as tripulacion_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(vuelos_bp, url_prefix='/api/vuelos')
    app.register_blueprint(aviones_bp, url_prefix='/api/aviones')
    app.register_blueprint(tripulacion_bp, url_prefix='/api/tripulacion')
    
    # --- 3. Ruta Raíz (Redirección al Login) ---
    @app.route('/')
    def index():
        return redirect(url_for('auth.login')) 
    # -------------------------------------------

    return app

# --- 4. Ejecución y Creación de Tablas ---

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all() 
    app.run(debug=True)