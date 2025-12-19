from flask import Flask, redirect, url_for
from config import Config
from models import db  # Importamos db desde el __init__.py de la carpeta models
from flask_login import LoginManager 

# --- 1. Inicialización de la Aplicación y Extensiones ---


# --- 1. Inicialización ---


class UserSimulado:
    def __init__(self, id):
        self.id = id
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    def get_id(self):
        return str(self.id)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app) 
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        # En lugar de buscar en la DB, devolvemos el usuario simulado
        # Esto evita que la app se rompa al no tener clase Usuario
        return UserSimulado(user_id)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar SQLAlchemy (ORM)
    db.init_app(app) 
    
    # Inicializar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return None

    # --- 2. Registro de Blueprints (Modularización) ---
    # Usamos importaciones locales para evitar registros circulares
    from blueprints.auth.auth import bp as auth_bp
    from blueprints.vuelos.vuelos import bp as vuelos_bp         
    from blueprints.aviones.aviones import bp as aviones_bp     
    from blueprints.tripulacion.tripulacion import bp as tripulacion_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(vuelos_bp, url_prefix='/vuelos')
    app.register_blueprint(aviones_bp, url_prefix='/aviones')
    app.register_blueprint(tripulacion_bp, url_prefix='/tripulacion')
    
    @app.route('/')
    def index():
        return redirect(url_for('auth.login')) 

    return app

# --- 4. Ejecución y Creación de Tablas ---

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # MEJORA: Importamos los modelos aquí dentro para que SQLAlchemy sepa qué tablas crear
        from models.vuelo import Vuelo, VueloTripulacion
        from models.avion import Avion
        from models.tripulante import Tripulante
        
        db.create_all() # Crea las tablas si no existen
        
    app.run(debug=True)