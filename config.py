import os

class Config:
    # Clave Secreta para seguridad de Flask y sesiones
    SECRET_KEY = os.environ.get('SECRET_KEY') or '272829' 
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:199535@localhost:3306/SkyTrack'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False