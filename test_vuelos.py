import unittest
from datetime import datetime
from app import create_app, db
from models import Vuelo, Avion

class TestVuelos(unittest.TestCase):
    def setUp(self):
        # Configuramos la app para pruebas
        self.app = create_app()
        # Usamos SQLite en memoria para que sea rápido y no ensucie tu DB real
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # 1. Creamos un avión de prueba
        a1 = Avion(modelo="Boeing 737", capacidad=150, estado="disponible")
        db.session.add(a1)
        db.session.commit()

        # 2. Creamos vuelos de prueba con todos los campos obligatorios
        # Agregamos capacidad_total y fecha_hora
        v1 = Vuelo(
            origen="Mendoza", 
            destino="Chile", 
            estado="Programado", 
            id_avion=a1.id, 
            baja_logica=False,
            capacidad_total=150,
            fecha_hora=datetime.now()
        )
        
        v2 = Vuelo(
            origen="Mendoza", 
            destino="Brasil", 
            estado="En vuelo", 
            id_avion=a1.id, 
            baja_logica=False,
            capacidad_total=150,
            fecha_hora=datetime.now()
        )
        
        v3 = Vuelo(
            origen="Buenos Aires", 
            destino="Chile", 
            estado="Programado", 
            id_avion=a1.id, 
            baja_logica=True, # Este simula un vuelo borrado
            capacidad_total=150,
            fecha_hora=datetime.now()
        )
        
        db.session.add_all([v1, v2, v3])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_filtro_por_estado(self):
        """Caso N° 7: Verificar que filtrar por estado devuelva solo los que coinciden"""
        vuelos = Vuelo.query.filter_by(estado="En vuelo").all()
        self.assertEqual(len(vuelos), 1)
        self.assertEqual(vuelos[0].destino, "Brasil")

    def test_filtro_por_origen(self):
        """Caso N° 7: Verificar que filtrar por origen excluya otros aeropuertos"""
        vuelos = Vuelo.query.filter(Vuelo.origen.ilike("%Mendoza%")).all()
        self.assertEqual(len(vuelos), 2)

    def test_vuelos_baja_logica_excluidos(self):
        """Caso N° 7: Verificar que vuelos con baja lógica no aparezcan"""
        vuelos_activos = Vuelo.query.filter_by(baja_logica=False).all()
        self.assertEqual(len(vuelos_activos), 2)
        for v in vuelos_activos:
            self.assertFalse(v.baja_logica)

if __name__ == '__main__':
    unittest.main()