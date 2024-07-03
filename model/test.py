from utils.db import db
from dataclasses import dataclass

@dataclass
class Test(db.Model):
    id_test: int = db.Column(db.Integer, primary_key=True)
    nombre: str = db.Column(db.String(100), nullable=False)
    descripcion: str = db.Column(db.Text)
    numero_preguntas: int = db.Column(db.Integer, nullable=False)

    def __init__(self, nombre, descripcion, numero_preguntas):
        self.nombre = nombre
        self.descripcion = descripcion
        self.numero_preguntas = numero_preguntas
