from werkzeug.security import generate_password_hash, check_password_hash
from utils.db import db
from dataclasses import dataclass

@dataclass
class Usuario(db.Model):
    id_usuario: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(100), nullable=False, unique=True)
    password: str = db.Column(db.String(255), nullable=False)
    id_persona: int = db.Column(db.Integer, db.ForeignKey('persona.id_persona'), nullable=False)

    def __init__(self, username, password, id_persona):
        self.username = username
        self.password = generate_password_hash(password)  
        self.id_persona = id_persona

    def check_password(self, password):
        return check_password_hash(self.password, password)
