from flask import Blueprint, request, jsonify
from model.persona import Persona
from utils.db import db

personas = Blueprint('personas', __name__)

@personas.route('/personas/v1', methods=['GET'])
def get_mensaje():
    result = {"data": 'Hola, Personas'}
    return jsonify(result)

@personas.route('/personas/v1/listar', methods=['GET'])
def listar_personas():
    personas = Persona.query.all()
    result = {
        "data": [persona.__dict__ for persona in personas],
        "status_code": 200,
        "msg": "Se recuperó la lista de Personas sin inconvenientes"
    }
    for persona in result["data"]:
        persona.pop('_sa_instance_state', None)  # Eliminar metadata de SQLAlchemy
    return jsonify(result), 200

@personas.route('/personas/v1/agregar', methods=['POST'])
def agregar_persona():
    data = request.json
    nueva_persona = Persona(
        apellido_paterno=data['apellido_paterno'],
        apellido_materno=data['apellido_materno'],
        nombres=data['nombres'],
        sexo=data['sexo'],
        telefono=data['telefono'],
        fecha_nacimiento=data['fecha_nacimiento'],
        id_ubigeo=data['id_ubigeo']
    )
    db.session.add(nueva_persona)
    db.session.commit()
    return jsonify({
        "status_code": 201,
        "msg": "Persona agregada exitosamente",
        "data": nueva_persona.__dict__
    }), 201

@personas.route('/personas/v1/actualizar/<int:id>', methods=['PUT'])
def actualizar_persona(id):
    data = request.json
    persona = Persona.query.get_or_404(id)
    persona.apellido_paterno = data.get('apellido_paterno', persona.apellido_paterno)
    persona.apellido_materno = data.get('apellido_materno', persona.apellido_materno)
    persona.nombres = data.get('nombres', persona.nombres)
    persona.sexo = data.get('sexo', persona.sexo)
    persona.telefono = data.get('telefono', persona.telefono)
    persona.fecha_nacimiento = data.get('fecha_nacimiento', persona.fecha_nacimiento)
    persona.id_ubigeo = data.get('id_ubigeo', persona.id_ubigeo)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Persona actualizada exitosamente",
        "data": persona.__dict__
    }), 200

@personas.route('/personas/v1/eliminar/<int:id>', methods=['DELETE'])
def eliminar_persona(id):
    persona = Persona.query.get_or_404(id)
    db.session.delete(persona)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Persona eliminada exitosamente"
    }), 200
