from flask import Blueprint, request, jsonify
from model.puntaje_opcion import PuntajeOpcion
from utils.db import db

puntajes_opciones = Blueprint('puntajes_opciones', __name__)

@puntajes_opciones.route('/puntajes_opciones/v1', methods=['GET'])
def get_mensaje():
    result = {"data": 'Hola, Puntajes Opciones'}
    return jsonify(result)

@puntajes_opciones.route('/puntajes_opciones/v1/listar', methods=['GET'])
def listar_puntajes_opciones():
    puntajes_opciones = PuntajeOpcion.query.all()
    result = {
        "data": [puntaje_opcion.__dict__ for puntaje_opcion in puntajes_opciones],
        "status_code": 200,
        "msg": "Se recuperó la lista de Puntajes Opciones sin inconvenientes"
    }
    for puntaje_opcion in result["data"]:
        puntaje_opcion.pop('_sa_instance_state', None)  # Eliminar metadata de SQLAlchemy
    return jsonify(result), 200

@puntajes_opciones.route('/puntajes_opciones/v1/agregar', methods=['POST'])
def agregar_puntaje_opcion():
    data = request.json
    nuevo_puntaje_opcion = PuntajeOpcion(
        id_pregunta=data['id_pregunta'],
        texto_opcion=data['texto_opcion'],
        puntaje=data['puntaje']
    )
    db.session.add(nuevo_puntaje_opcion)
    db.session.commit()
    return jsonify({
        "status_code": 201,
        "msg": "Puntaje Opción agregado exitosamente",
        "data": nuevo_puntaje_opcion.__dict__
    }), 201

@puntajes_opciones.route('/puntajes_opciones/v1/actualizar/<int:id>', methods=['PUT'])
def actualizar_puntaje_opcion(id):
    data = request.json
    puntaje_opcion = PuntajeOpcion.query.get_or_404(id)
    puntaje_opcion.id_pregunta = data.get('id_pregunta', puntaje_opcion.id_pregunta)
    puntaje_opcion.texto_opcion = data.get('texto_opcion', puntaje_opcion.texto_opcion)
    puntaje_opcion.puntaje = data.get('puntaje', puntaje_opcion.puntaje)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Puntaje Opción actualizado exitosamente",
        "data": puntaje_opcion.__dict__
    }), 200

@puntajes_opciones.route('/puntajes_opciones/v1/eliminar/<int:id>', methods=['DELETE'])
def eliminar_puntaje_opcion(id):
    puntaje_opcion = PuntajeOpcion.query.get_or_404(id)
    db.session.delete(puntaje_opcion)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Puntaje Opción eliminado exitosamente"
    }), 200
