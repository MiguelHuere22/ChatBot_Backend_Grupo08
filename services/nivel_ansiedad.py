from flask import Blueprint, request, jsonify
from model.nivel_ansiedad import NivelAnsiedad
from utils.db import db

nivelansiedades = Blueprint('nivelansiedades', __name__)

@nivelansiedades.route('/nivelansiedades/v1', methods=['GET'])
def get_mensaje():
    result = {"data": 'Hola, NivelAnsiedades'}
    return jsonify(result)

@nivelansiedades.route('/nivelansiedades/v1/listar', methods=['GET'])
def listar_nivelansiedades():
    niveles = NivelAnsiedad.query.all()
    result = {
        "data": [nivel.to_dict() for nivel in niveles],
        "status_code": 200,
        "msg": "Se recuperó la lista de Niveles de Ansiedad sin inconvenientes"
    }
    return jsonify(result), 200

@nivelansiedades.route('/nivelansiedades/v1/agregar', methods=['POST'])
def agregar_nivelansiedad():
    data = request.json
    nuevo_nivel = NivelAnsiedad(
        descripcion=data['descripcion'],
        fundamentacion_cientifica=data['fundamentacion_cientifica']
    )
    db.session.add(nuevo_nivel)
    db.session.commit()
    return jsonify({
        "status_code": 201,
        "msg": "Nivel de Ansiedad agregado exitosamente",
        "data": nuevo_nivel.to_dict()
    }), 201