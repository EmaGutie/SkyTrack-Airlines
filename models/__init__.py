from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


from .avion import Avion
from .vuelo import Vuelo, VueloTripulacion
from .tripulante import Tripulante