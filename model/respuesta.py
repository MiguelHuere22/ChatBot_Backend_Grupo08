from utils.db import db
from dataclasses import dataclass

@dataclass
class Respuesta(db.Model):
    id_respuesta: int = db.Column(db.Integer, primary_key=True)
    id_persona: int = db.Column(db.Integer, db.ForeignKey('persona.id_persona'), nullable=False)
    id_opcion: int = db.Column(db.Integer, db.ForeignKey('puntaje_opcion.id_opcion'), nullable=False)

    def __init__(self, id_persona, id_opcion):
        self.id_persona = id_persona
        self.id_opcion = id_opcion
