from flask import Blueprint, request, jsonify
from model.observacion import Observacion
from model.nivel_ansiedad import NivelAnsiedad  # Importa el modelo NivelAnsiedad
from utils.db import db

observaciones = Blueprint('observaciones', __name__)

@observaciones.route('/observaciones/v1', methods=['GET'])
def get_mensaje():
    result = {"data": 'Hola, Observaciones'}
    return jsonify(result)

@observaciones.route('/observaciones/v1/listar', methods=['GET'])
def listar_observaciones():
    observaciones = Observacion.query.all()
    result = {
        "data": [observacion.to_dict() for observacion in observaciones],
        "status_code": 200,
        "msg": "Se recuperó la lista de Observaciones sin inconvenientes"
    }
    return jsonify(result), 200

@observaciones.route('/observaciones/v1/agregar', methods=['POST'])
def agregar_observacion():
    data = request.json

    # Depuración: Imprimir todos los niveles de ansiedad disponibles
    nivel_ansiedad = NivelAnsiedad.query.all()
    print("Niveles de ansiedad disponibles en la base de datos:")
    for nivel in nivel_ansiedad:
        print(f"- '{nivel.descripcion}' (ID: {nivel.id_nivel_ansiedad})")

    # Depuración: Imprimir nivel de ansiedad recibido
    print(f"Nivel de ansiedad recibido: '{data['nivel_ansiedad']}'")

    # Buscar el ID de nivel_ansiedad basado en la descripción
    nivel_ansiedad = data['nivel_ansiedad']
    
    # Generar y ejecutar la consulta SQL directamente
    sql_query = NivelAnsiedad.query.filter_by(descripcion=nivel_ansiedad).statement
    print(f"Consulta SQL generada: {sql_query}")
    nivel_ansiedad_obj = NivelAnsiedad.query.filter_by(descripcion=nivel_ansiedad).first()

    # Depuración: Imprimir objeto encontrado
    print(f"Objeto nivel_ansiedad encontrado: {nivel_ansiedad_obj}")

    if not nivel_ansiedad_obj:
        return jsonify({
            "status_code": 400,
            "msg": "El nivel de ansiedad proporcionado no es válido"
        }), 400

    nueva_observacion = Observacion(
        id_puntuacion=data['id_puntuacion'],
        id_especialista=data['id_especialista'],
        observaciones=data['observaciones'],
        id_nivel_ansiedad=nivel_ansiedad_obj.id_nivel_ansiedad,  # Usar el ID de nivel_ansiedad
        solicitud_cita=data['solicitud_cita'],
        tratamiento=data.get('tratamiento', '')  # Incluir tratamiento
    )
    db.session.add(nueva_observacion)
    db.session.commit()
    return jsonify({
        "status_code": 201,
        "msg": "Observación agregada exitosamente",
        "data": nueva_observacion.to_dict()
    }), 201

@observaciones.route('/observaciones/v1/actualizar/<int:id>', methods=['PUT'])
def actualizar_observacion(id):
    data = request.json
    observacion = Observacion.query.get_or_404(id)

    # Buscar el ID de nivel_ansiedad basado en la descripción si es proporcionado
    if 'nivel_ansiedad' in data:
        nivel_ansiedad = data['nivel_ansiedad']
        nivel_ansiedad_obj = NivelAnsiedad.query.filter_by(descripcion=nivel_ansiedad).first()
        
        # Depuración: Imprimir objeto encontrado
        print(f"Objeto nivel_ansiedad encontrado: {nivel_ansiedad_obj}")

        if not nivel_ansiedad_obj:
            return jsonify({
                "status_code": 400,
                "msg": "El nivel de ansiedad proporcionado no es válido"
            }), 400
        observacion.id_nivel_ansiedad = nivel_ansiedad_obj.id_nivel_ansiedad

    observacion.id_puntuacion = data.get('id_puntuacion', observacion.id_puntuacion)
    observacion.id_especialista = data.get('id_especialista', observacion.id_especialista)
    observacion.observaciones = data.get('observaciones', observacion.observaciones)
    observacion.solicitud_cita = data.get('solicitud_cita', observacion.solicitud_cita)
    observacion.tratamiento = data.get('tratamiento', observacion.tratamiento)  # Actualizar tratamiento si es proporcionado

    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Observación actualizada exitosamente",
        "data": observacion.to_dict()
    }), 200

@observaciones.route('/observaciones/v1/eliminar/<int:id>', methods=['DELETE'])
def eliminar_observacion(id):
    observacion = Observacion.query.get_or_404(id)
    db.session.delete(observacion)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Observación eliminada exitosamente"
    }), 200
