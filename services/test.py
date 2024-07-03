from flask import Blueprint, request, jsonify
from model.test import Test
from utils.db import db

tests = Blueprint('tests', __name__)

@tests.route('/tests/v1', methods=['GET'])
def get_mensaje():
    result = {"data": 'Hola, Tests'}
    return jsonify(result)

@tests.route('/tests/v1/listar', methods=['GET'])
def listar_tests():
    tests = Test.query.all()
    result = {
        "data": [test.__dict__ for test in tests],
        "status_code": 200,
        "msg": "Se recuperó la lista de Tests sin inconvenientes"
    }
    for test in result["data"]:
        test.pop('_sa_instance_state', None)  # Eliminar metadata de SQLAlchemy
    return jsonify(result), 200

@tests.route('/tests/v1/agregar', methods=['POST'])
def agregar_test():
    data = request.json
    nuevo_test = Test(
        nombre=data['nombre'],
        descripcion=data['descripcion'],
        numero_preguntas=data['numero_preguntas']
    )
    db.session.add(nuevo_test)
    db.session.commit()
    return jsonify({
        "status_code": 201,
        "msg": "Test agregado exitosamente",
        "data": nuevo_test.__dict__
    }), 201

@tests.route('/tests/v1/actualizar/<int:id>', methods=['PUT'])
def actualizar_test(id):
    data = request.json
    test = Test.query.get_or_404(id)
    test.nombre = data.get('nombre', test.nombre)
    test.descripcion = data.get('descripcion', test.descripcion)
    test.numero_preguntas = data.get('numero_preguntas', test.numero_preguntas)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Test actualizado exitosamente",
        "data": test.__dict__
    }), 200

@tests.route('/tests/v1/eliminar/<int:id>', methods=['DELETE'])
def eliminar_test(id):
    test = Test.query.get_or_404(id)
    db.session.delete(test)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Test eliminado exitosamente"
    }), 200
