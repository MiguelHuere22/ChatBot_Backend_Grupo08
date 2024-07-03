from flask import Blueprint, request, jsonify
from model.rol import Rol
from utils.db import db

roles = Blueprint('roles', __name__)

@roles.route('/roles/v1', methods=['GET'])
def get_mensaje():
    result = {"data": 'Hola, Roles'}
    return jsonify(result)

@roles.route('/roles/v1/listar', methods=['GET'])
def listar_roles():
    roles = Rol.query.all()
    result = {
        "data": [rol.__dict__ for rol in roles],
        "status_code": 200,
        "msg": "Se recuperó la lista de Roles sin inconvenientes"
    }
    for rol in result["data"]:
        rol.pop('_sa_instance_state', None)  # Eliminar metadata de SQLAlchemy
    return jsonify(result), 200

@roles.route('/roles/v1/agregar', methods=['POST'])
def agregar_rol():
    data = request.json
    nuevo_rol = Rol(tipo_rol=data['tipo_rol'])
    db.session.add(nuevo_rol)
    db.session.commit()
    return jsonify({
        "status_code": 201,
        "msg": "Rol agregado exitosamente",
        "data": nuevo_rol.__dict__
    }), 201

@roles.route('/roles/v1/actualizar/<int:id>', methods=['PUT'])
def actualizar_rol(id):
    data = request.json
    rol = Rol.query.get_or_404(id)
    rol.tipo_rol = data.get('tipo_rol', rol.tipo_rol)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Rol actualizado exitosamente",
        "data": rol.__dict__
    }), 200

@roles.route('/roles/v1/eliminar/<int:id>', methods=['DELETE'])
def eliminar_rol(id):
    rol = Rol.query.get_or_404(id)
    db.session.delete(rol)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Rol eliminado exitosamente"
    }), 200
