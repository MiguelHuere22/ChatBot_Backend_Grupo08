from flask import Blueprint, request, jsonify
from model.recomendacion import Recomendacion
from utils.db import db

recomendaciones = Blueprint('recomendaciones', __name__)

@recomendaciones.route('/recomendaciones/v1', methods=['GET'])
def get_mensaje():
    result = {"data": 'Hola, Recomendaciones'}
    return jsonify(result)

@recomendaciones.route('/recomendaciones/v1/listar', methods=['GET'])
def listar_recomendaciones():
    recomendaciones = Recomendacion.query.all()
    result = {
        "data": [recomendacion.__dict__ for recomendacion in recomendaciones],
        "status_code": 200,
        "msg": "Se recuperó la lista de Recomendaciones sin inconvenientes"
    }
    for recomendacion in result["data"]:
        recomendacion.pop('_sa_instance_state', None)  # Eliminar metadata de SQLAlchemy
    return jsonify(result), 200

@recomendaciones.route('/recomendaciones/v1/agregar', methods=['POST'])
def agregar_recomendacion():
    data = request.json
    nueva_recomendacion = Recomendacion(
        descripcion=data['descripcion']
    )
    db.session.add(nueva_recomendacion)
    db.session.commit()
    return jsonify({
        "status_code": 201,
        "msg": "Recomendación agregada exitosamente",
        "data": nueva_recomendacion.__dict__
    }), 201

@recomendaciones.route('/recomendaciones/v1/actualizar/<int:id>', methods=['PUT'])
def actualizar_recomendacion(id):
    data = request.json
    recomendacion = Recomendacion.query.get_or_404(id)
    recomendacion.descripcion = data.get('descripcion', recomendacion.descripcion)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Recomendación actualizada exitosamente",
        "data": recomendacion.__dict__
    }), 200

@recomendaciones.route('/recomendaciones/v1/eliminar/<int:id>', methods=['DELETE'])
def eliminar_recomendacion(id):
    recomendacion = Recomendacion.query.get_or_404(id)
    db.session.delete(recomendacion)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Recomendación eliminada exitosamente"
    }), 200
