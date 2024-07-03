from utils.db import db
from dataclasses import dataclass

@dataclass
class PuntajeOpcion(db.Model):
    id_opcion: int = db.Column(db.Integer, primary_key=True)
    id_pregunta: int = db.Column(db.Integer, db.ForeignKey('pregunta.id_pregunta'), nullable=False)
    texto_opcion: str = db.Column(db.Text, nullable=False)
    puntaje: int = db.Column(db.Integer, nullable=False)

    def __init__(self, id_pregunta, texto_opcion, puntaje):
        self.id_pregunta = id_pregunta
        self.texto_opcion = texto_opcion
        self.puntaje = puntaje
