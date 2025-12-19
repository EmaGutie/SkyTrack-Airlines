from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash # Para contraseñas seguras

db = SQLAlchemy()


class Usuario(db.Model, UserMixin): 
    # Roles: 'admin', 'operador'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    rol = db.Column(db.String(50), nullable=False) 
    password_hash = db.Column(db.String(200), nullable=False) 

    def set_password(self, password):
        """Hashea y guarda la contraseña."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la contraseña ingresada con el hash."""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Método helper para chequear el rol."""
        return self.rol == 'admin'

    def is_operador(self):
        """Método helper para chequear el rol."""
        return self.rol == 'operador'

class Avion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(100), nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(50), default='disponible')
    baja_logica = db.Column(db.Boolean, default=False)
    vuelos = db.relationship('Vuelo', backref='avion', lazy=True)

class Vuelo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    capacidad_total = db.Column(db.Integer, nullable=False)
    origen = db.Column(db.String(100), nullable=False) 
    destino = db.Column(db.String(100), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False) 
    id_avion = db.Column(db.Integer, db.ForeignKey('avion.id'), nullable=False) 
    estado = db.Column(db.String(50), default='programado') 
    baja_logica = db.Column(db.Boolean, default=False) 
    tripulacion_vuelos = db.relationship('VueloTripulacion', backref='vuelo_real', lazy=True)

class Tripulante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(50), nullable=False)
    baja_logica = db.Column(db.Boolean, default=False)
    vuelos_asignados = db.relationship('VueloTripulacion', backref='tripulante_real', lazy=True)
    

class VueloTripulacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_vuelo = db.Column(db.Integer, db.ForeignKey('vuelo.id'), nullable=False)
    id_tripulante = db.Column(db.Integer, db.ForeignKey('tripulante.id'), nullable=False)
    