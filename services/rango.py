from flask import Blueprint, request, jsonify
from model.rango import Rango
from utils.db import db

rangos = Blueprint('rangos', __name__)

@rangos.route('/rangos/v1', methods=['GET'])
def get_mensaje():
    result = {"data": 'Hola, Rangos'}
    return jsonify(result)

@rangos.route('/rangos/v1/listar', methods=['GET'])
def listar_rangos():
    rangos = Rango.query.all()
    result = {
        "data": [rango.__dict__ for rango in rangos],
        "status_code": 200,
        "msg": "Se recuperó la lista de Rangos sin inconvenientes"
    }
    for rango in result["data"]:
        rango.pop('_sa_instance_state', None)  # Eliminar metadata de SQLAlchemy
    return jsonify(result), 200

@rangos.route('/rangos/v1/agregar', methods=['POST'])
def agregar_rango():
    data = request.json
    nuevo_rango = Rango(
        id_test=data['id_test'],
        rango_min=data['rango_min'],
        rango_max=data['rango_max'],
        interpretacion=data['interpretacion']
    )
    db.session.add(nuevo_rango)
    db.session.commit()
    return jsonify({
        "status_code": 201,
        "msg": "Rango agregado exitosamente",
        "data": nuevo_rango.__dict__
    }), 201

@rangos.route('/rangos/v1/actualizar/<int:id>', methods=['PUT'])
def actualizar_rango(id):
    data = request.json
    rango = Rango.query.get_or_404(id)
    rango.id_test = data.get('id_test', rango.id_test)
    rango.rango_min = data.get('rango_min', rango.rango_min)
    rango.rango_max = data.get('rango_max', rango.rango_max)
    rango.interpretacion = data.get('interpretacion', rango.interpretacion)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Rango actualizado exitosamente",
        "data": rango.__dict__
    }), 200

@rangos.route('/rangos/v1/eliminar/<int:id>', methods=['DELETE'])
def eliminar_rango(id):
    rango = Rango.query.get_or_404(id)
    db.session.delete(rango)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Rango eliminado exitosamente"
    }), 200
