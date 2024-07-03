from flask import Blueprint, request, jsonify
from model.ubigeo import Ubigeo
from utils.db import db

ubigeos = Blueprint('ubigeos', __name__)

@ubigeos.route('/ubigeos/v1', methods=['GET'])
def get_mensaje():
    result = {"data": 'Hola, Ubigeos'}
    return jsonify(result)

@ubigeos.route('/ubigeos/v1/listar', methods=['GET'])
def listar_ubigeos():
    ubigeos = Ubigeo.query.all()
    result = {
        "data": [ubigeo.__dict__ for ubigeo in ubigeos],
        "status_code": 200,
        "msg": "Se recuperó la lista de Ubigeos sin inconvenientes"
    }
    for ubigeo in result["data"]:
        ubigeo.pop('_sa_instance_state', None)  # Eliminar metadata de SQLAlchemy
    return jsonify(result), 200

@ubigeos.route('/ubigeos/v1/agregar', methods=['POST'])
def agregar_ubigeo():
    data = request.json
    nuevo_ubigeo = Ubigeo(
        id_ubigeo=data['id_ubigeo'],
        departamento=data['departamento'],
        provincia=data['provincia'],
        distrito=data['distrito'],
        superficie=data['superficie'],
        poblacion=data['poblacion'],
        latitud=data['latitud'],
        longitud=data['longitud']
    )
    db.session.add(nuevo_ubigeo)
    db.session.commit()
    return jsonify({
        "status_code": 201,
        "msg": "Ubigeo agregado exitosamente",
        "data": nuevo_ubigeo.__dict__
    }), 201

@ubigeos.route('/ubigeos/v1/actualizar/<string:id>', methods=['PUT'])
def actualizar_ubigeo(id):
    data = request.json
    ubigeo = Ubigeo.query.get_or_404(id)
    ubigeo.departamento = data.get('departamento', ubigeo.departamento)
    ubigeo.provincia = data.get('provincia', ubigeo.provincia)
    ubigeo.distrito = data.get('distrito', ubigeo.distrito)
    ubigeo.superficie = data.get('superficie', ubigeo.superficie)
    ubigeo.poblacion = data.get('poblacion', ubigeo.poblacion)
    ubigeo.latitud = data.get('latitud', ubigeo.latitud)
    ubigeo.longitud = data.get('longitud', ubigeo.longitud)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Ubigeo actualizado exitosamente",
        "data": ubigeo.__dict__
    }), 200

@ubigeos.route('/ubigeos/v1/eliminar/<string:id>', methods=['DELETE'])
def eliminar_ubigeo(id):
    ubigeo = Ubigeo.query.get_or_404(id)
    db.session.delete(ubigeo)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Ubigeo eliminado exitosamente"
    }), 200
