from utils.db import db
from dataclasses import dataclass

@dataclass
class Area(db.Model):
    id_area: int = db.Column(db.Integer, primary_key=True)
    nombre: str = db.Column(db.String(50), nullable=False)

    def __init__(self, nombre):
        self.nombre = nombre



