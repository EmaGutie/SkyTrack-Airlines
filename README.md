#  SkyTrack Airlines - Sistema de Gestión de Vuelos

Este proyecto es una aplicación web desarrollada en Python con Flask para la gestión integral de vuelos, aviones y tripulación, cumpliendo con los requisitos del examen final de Programación II.

##  Funcionalidades Principales
- **Gestión de Vuelos:** Visualización, filtrado y creación de vuelos.
- **Panel de Seguimiento:** Interfaz en tiempo real para el control de estados de vuelo (Programado, En Vuelo, Arribado).
- **Gestión de Tripulación:** Asignación de personal a vuelos específicos (Rol Operador).
- **Seguridad:** Sistema de autenticación con roles (Administrador y Operador).

##  Instalación y Configuración

1. **Clonar el repositorio o extraer el ZIP.**
2. **Crear un entorno virtual:**
   ```bash
   python -m venv venv




Activar el entorno virtual:

Windows: .\venv\Scripts\activate

Linux/Mac: source venv/bin/activate

Instalar dependencias:

Bash

pip install -r requeriments.txt
Ejecutar la aplicación:

Bash

python app.py 
Credenciales de Acceso (Roles)
Administrador: Usuario: admin | Password: adminpassword

Operador: Usuario: operador | Password: operadorpassword

Pruebas de Calidad (Testing)
El sistema cuenta con una suite de pruebas automatizadas que validan tanto la lógica interna como el flujo de usuario:

1. Test Unitarios (Caso N° 7)
Prueba la lógica de filtrado de vuelos y validaciones de modelos.

Ejecución: python test_vuelos.py

2. Test End-to-End (Caso N° 8)
Simula un flujo completo: Login -> Ver Listado -> Acceder al Panel -> Cambiar Estado de Vuelo.

Ejecución: python test_e2e.py

Tecnologías Utilizadas
Backend: Flask

Base de Datos: MySQL (Producción) / SQLite (Testing)

ORM: SQLAlchemy

Autenticación: Flask-Login

Frontend: Jinja2 Templates & CSS Personalizado


