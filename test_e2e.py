import unittest
from datetime import datetime
from app import create_app, db
from models import Vuelo, Avion, Usuario

class TestE2E(unittest.TestCase):
    def setUp(self):
        # Configuramos la app para el test
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False 
        
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        # Crea las tablas en la base de datos temporal
        db.create_all()

        test_user = Usuario(username='admin_final_test', rol='admin')
        test_user.set_password('admin123')
        
        # 2. Crear un avión necesario para la FK del vuelo
        avion_test = Avion(modelo="Boeing 747 Test", capacidad=150, estado="disponible")
        
        db.session.add(test_user)
        db.session.add(avion_test)
        db.session.commit()

        # 3. Crear el vuelo con todos los campos obligatorios (Caso N° 8)
        vuelo_test = Vuelo(
            origen="Mendoza", 
            destino="Buenos Aires", 
            estado="Programado", 
            id_avion=avion_test.id, 
            capacidad_total=150, 
            fecha_hora=datetime.now(), 
            baja_logica=False
        )
        db.session.add(vuelo_test)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_flujo_principal_usuario(self):
        """
        Caso N° 8: Test End-to-End
        Verifica: Login -> Listado -> Panel -> Cambio de Estado
        """
        
        # 1. LOGIN: Entrar al sitio
        login_response = self.client.post('/auth/login', data={
            'username': 'admin_final_test', 
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(login_response.status_code, 200)

        # 2. LISTADO: Ver que los vuelos carguen correctamente
        listado_response = self.client.get('/api/vuelos/')
        self.assertEqual(listado_response.status_code, 200)
        self.assertIn(b'Mendoza', listado_response.data)

        # 3. PANEL: Verificar acceso al panel de seguimiento
        panel_response = self.client.get('/api/vuelos/panel-estado')
        self.assertEqual(panel_response.status_code, 200)
        self.assertIn(b'Panel', panel_response.data) 

        # 4. CAMBIO DE ESTADO: Simular la acción de "Iniciar Vuelo"
        vuelo = Vuelo.query.filter_by(origen="Mendoza").first()
        
        # Usamos la ruta de actualización de estado que definimos antes
        url_update = f'/api/vuelos/actualizar-estado/{vuelo.id}/En vuelo'
        update_response = self.client.post(url_update, follow_redirects=True)
        self.assertEqual(update_response.status_code, 200)
        
        # Verificamos que el cambio impactó en la base de datos
        db.session.refresh(vuelo)
        self.assertEqual(vuelo.estado, 'En vuelo')

if __name__ == '__main__':
    unittest.main()