from . import db

class Tripulante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(50), nullable=False)
    baja_logica = db.Column(db.Boolean, default=False)
    vuelos_asignados = db.relationship('VueloTripulacion', backref='tripulante_real', lazy=True)