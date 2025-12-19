from . import db

class Avion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(100), nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(50), default='disponible')
    baja_logica = db.Column(db.Boolean, default=False)
    vuelos = db.relationship('Vuelo', backref='avion', lazy=True)