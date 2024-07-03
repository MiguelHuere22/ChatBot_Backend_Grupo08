from utils.db import db
from dataclasses import dataclass

@dataclass
class Ubigeo(db.Model):
    id_ubigeo: str = db.Column(db.String(6), primary_key=True)
    departamento: str = db.Column(db.String(50), nullable=False)
    provincia: str = db.Column(db.String(50))
    distrito: str = db.Column(db.String(50))
    superficie: float = db.Column(db.Numeric)
    poblacion: int = db.Column(db.Integer)
    latitud: float = db.Column(db.Numeric)
    longitud: float = db.Column(db.Numeric)

    def __init__(self, id_ubigeo, departamento, provincia, distrito, superficie, poblacion, latitud, longitud):
        self.id_ubigeo = id_ubigeo
        self.departamento = departamento
        self.provincia = provincia
        self.distrito = distrito
        self.superficie = superficie
        self.poblacion = poblacion
        self.latitud = latitud
        self.longitud = longitud

