from utils.db import db
from dataclasses import dataclass

@dataclass
class NivelAnsiedad(db.Model):
    id_nivel_ansiedad: int = db.Column(db.Integer, primary_key=True)
    descripcion: str = db.Column(db.String(150), nullable=False)
    fundamentacion_cientifica: str = db.Column(db.String(500), nullable=True)  # Nueva columna

    def __init__(self, descripcion, fundamentacion_cientifica):
        self.descripcion = descripcion
        self.fundamentacion_cientifica = fundamentacion_cientifica

    def to_dict(self):
        return {
            "id_nivel_ansiedad": self.id_nivel_ansiedad,
            "descripcion": self.descripcion,
            "fundamentacion_cientifica": self.fundamentacion_cientifica
        }
