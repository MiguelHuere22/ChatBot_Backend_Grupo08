from utils.db import db
from dataclasses import dataclass

@dataclass
class Rol(db.Model):
    id_rol: int = db.Column(db.Integer, primary_key=True)
    tipo_rol: str = db.Column(db.String(50), nullable=False)

    def __init__(self, tipo_rol):
        self.tipo_rol = tipo_rol
