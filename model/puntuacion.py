from utils.db import db
from dataclasses import dataclass

@dataclass
class Puntuacion(db.Model):
    id_puntuacion: int = db.Column(db.Integer, primary_key=True)
    puntaje_total: int = db.Column(db.Integer, nullable=False)
    id_persona: int = db.Column(db.Integer, db.ForeignKey('persona.id_persona'), nullable=False)
    id_test: int = db.Column(db.Integer, db.ForeignKey('test.id_test'), nullable=False)
    fecha: str = db.Column(db.Date, nullable=False)
    id_interpretacion: int = db.Column(db.Integer, db.ForeignKey('rango.id_rango'), nullable=False)

    def __init__(self, puntaje_total, id_persona, id_test, fecha, id_interpretacion):
        self.puntaje_total = puntaje_total
        self.id_persona = id_persona
        self.id_test = id_test
        self.fecha = fecha
        self.id_interpretacion = id_interpretacion

