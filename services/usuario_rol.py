from flask import Blueprint, request, jsonify
from model.usuario_rol import UsuarioRol
from utils.db import db

usuarios_roles = Blueprint('usuarios_roles', __name__)

@usuarios_roles.route('/usuarios_roles/v1', methods=['GET'])
def get_mensaje():
    result = {"data": 'Hola, Usuarios Roles'}
    return jsonify(result)

@usuarios_roles.route('/usuarios_roles/v1/listar', methods=['GET'])
def listar_usuarios_roles():
    usuarios_roles = UsuarioRol.query.all()
    result = {
        "data": [usuario_rol.__dict__ for usuario_rol in usuarios_roles],
        "status_code": 200,
        "msg": "Se recuperó la lista de Usuarios Roles sin inconvenientes"
    }
    for usuario_rol in result["data"]:
        usuario_rol.pop('_sa_instance_state', None)  # Eliminar metadata de SQLAlchemy
    return jsonify(result), 200

@usuarios_roles.route('/usuarios_roles/v1/agregar', methods=['POST'])
def agregar_usuario_rol():
    data = request.json
    nuevo_usuario_rol = UsuarioRol(
        id_usuario=data['id_usuario'],
        id_rol=data['id_rol']
    )
    db.session.add(nuevo_usuario_rol)
    db.session.commit()
    return jsonify({
        "status_code": 201,
        "msg": "Usuario Rol agregado exitosamente",
        "data": nuevo_usuario_rol.__dict__
    }), 201

@usuarios_roles.route('/usuarios_roles/v1/actualizar/<int:id_usuario>/<int:id_rol>', methods=['PUT'])
def actualizar_usuario_rol(id_usuario, id_rol):
    data = request.json
    usuario_rol = UsuarioRol.query.get_or_404((id_usuario, id_rol))
    usuario_rol.id_usuario = data.get('id_usuario', usuario_rol.id_usuario)
    usuario_rol.id_rol = data.get('id_rol', usuario_rol.id_rol)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Usuario Rol actualizado exitosamente",
        "data": usuario_rol.__dict__
    }), 200

@usuarios_roles.route('/usuarios_roles/v1/eliminar/<int:id_usuario>/<int:id_rol>', methods=['DELETE'])
def eliminar_usuario_rol(id_usuario, id_rol):
    usuario_rol = UsuarioRol.query.get_or_404((id_usuario, id_rol))
    db.session.delete(usuario_rol)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Usuario Rol eliminado exitosamente"
    }), 200
