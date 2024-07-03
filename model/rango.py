from utils.db import db
from dataclasses import dataclass

@dataclass
class Rango(db.Model):
    id_rango: int = db.Column(db.Integer, primary_key=True)
    id_test: int = db.Column(db.Integer, db.ForeignKey('test.id_test'), nullable=False)
    rango_min: int = db.Column(db.Integer, nullable=False)
    rango_max: int = db.Column(db.Integer, nullable=False)
    interpretacion: str = db.Column(db.Text)

    def __init__(self, id_test, rango_min, rango_max, interpretacion):
        self.id_test = id_test
        self.rango_min = rango_min
        self.rango_max = rango_max
        self.interpretacion = interpretacion

