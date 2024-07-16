from utils.db import db
from datetime import datetime

class Conversacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    titulo = db.Column(db.String(255))
    contenido = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.Date, nullable=False, default=datetime.now().date)
    hora = db.Column(db.Time, nullable=False, default=datetime.now().time)

    def __init__(self, id_usuario, titulo, contenido):
        self.id_usuario = id_usuario
        self.titulo = titulo
        self.contenido = contenido
        self.fecha = datetime.now().date()
        self.hora = datetime.now().time()

