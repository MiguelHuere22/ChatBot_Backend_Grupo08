from flask import Blueprint, request, jsonify
from model.pregunta import Pregunta
from utils.db import db

preguntas = Blueprint('preguntas', __name__)

@preguntas.route('/preguntas/v1', methods=['GET'])
def get_mensaje():
    result = {"data": 'Hola, Preguntas'}
    return jsonify(result)

@preguntas.route('/preguntas/v1/listar', methods=['GET'])
def listar_preguntas():
    preguntas = Pregunta.query.all()
    result = {
        "data": [pregunta.__dict__ for pregunta in preguntas],
        "status_code": 200,
        "msg": "Se recuperó la lista de Preguntas sin inconvenientes"
    }
    for pregunta in result["data"]:
        pregunta.pop('_sa_instance_state', None)  # Eliminar metadata de SQLAlchemy
    return jsonify(result), 200

@preguntas.route('/preguntas/v1/agregar', methods=['POST'])
def agregar_pregunta():
    data = request.json
    nueva_pregunta = Pregunta(
        texto=data['texto'],
        id_test=data['id_test'],
        id_area=data['id_area']
    )
    db.session.add(nueva_pregunta)
    db.session.commit()
    return jsonify({
        "status_code": 201,
        "msg": "Pregunta agregada exitosamente",
        "data": nueva_pregunta.__dict__
    }), 201

@preguntas.route('/preguntas/v1/actualizar/<int:id>', methods=['PUT'])
def actualizar_pregunta(id):
    data = request.json
    pregunta = Pregunta.query.get_or_404(id)
    pregunta.texto = data.get('texto', pregunta.texto)
    pregunta.id_test = data.get('id_test', pregunta.id_test)
    pregunta.id_area = data.get('id_area', pregunta.id_area)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Pregunta actualizada exitosamente",
        "data": pregunta.__dict__
    }), 200

@preguntas.route('/preguntas/v1/eliminar/<int:id>', methods=['DELETE'])
def eliminar_pregunta(id):
    pregunta = Pregunta.query.get_or_404(id)
    db.session.delete(pregunta)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Pregunta eliminada exitosamente"
    }), 200
