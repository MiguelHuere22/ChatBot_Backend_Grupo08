from utils.db import db
from dataclasses import dataclass

@dataclass
class UsuarioRol(db.Model):
    id_usuario: int = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), primary_key=True)
    id_rol: int = db.Column(db.Integer, db.ForeignKey('rol.id_rol'), primary_key=True)

    def __init__(self, id_usuario, id_rol):
        self.id_usuario = id_usuario
        self.id_rol = id_rol
