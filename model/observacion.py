from utils.db import db
from dataclasses import dataclass

@dataclass
class Observacion(db.Model):
    id_observacion: int = db.Column(db.Integer, primary_key=True)
    id_puntuacion: int = db.Column(db.Integer, db.ForeignKey('puntuacion.id_puntuacion'), nullable=False)
    id_especialista: int = db.Column(db.Integer, db.ForeignKey('persona.id_persona'), nullable=False)
    observaciones: str = db.Column(db.String(550))
    id_nivel_ansiedad: int = db.Column(db.Integer, db.ForeignKey('nivel_ansiedad.id_nivel_ansiedad'), nullable=False)  # Foreign key reference
    solicitud_cita: str = db.Column(db.String(2), nullable=False)
    tratamiento: str = db.Column(db.String(6000))  # Nueva columna tratamiento

    def __init__(self, id_puntuacion, id_especialista, observaciones, id_nivel_ansiedad, solicitud_cita, tratamiento):
        self.id_puntuacion = id_puntuacion
        self.id_especialista = id_especialista
        self.observaciones = observaciones
        self.id_nivel_ansiedad = id_nivel_ansiedad  # Asignación del nuevo parámetro id_nivel_ansiedad
        self.solicitud_cita = solicitud_cita
        self.tratamiento = tratamiento

    def to_dict(self):
        return {
            "id_observacion": self.id_observacion,
            "id_puntuacion": self.id_puntuacion,
            "id_especialista": self.id_especialista,
            "observaciones": self.observaciones,
            "id_nivel_ansiedad": self.id_nivel_ansiedad,  # Inclusión de id_nivel_ansiedad en el diccionario
            "solicitud_cita": self.solicitud_cita,
            "tratamiento": self.tratamiento  # Inclusión de tratamiento en el diccionario
        }
