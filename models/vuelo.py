from . import db

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

class VueloTripulacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_vuelo = db.Column(db.Integer, db.ForeignKey('vuelo.id'), nullable=False)
    id_tripulante = db.Column(db.Integer, db.ForeignKey('tripulante.id'), nullable=False)