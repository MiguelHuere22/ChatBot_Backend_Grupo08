from utils.db import db
from dataclasses import dataclass

@dataclass
class Recomendacion(db.Model):
    id_recomendacion: int = db.Column(db.Integer, primary_key=True)
    descripcion: str = db.Column(db.String(255), nullable=False)

    def __init__(self, descripcion):
        self.descripcion = descripcion
