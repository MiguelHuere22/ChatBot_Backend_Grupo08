from flask import Blueprint, request, jsonify
from model.puntuacion import Puntuacion
from model.respuesta import Respuesta
from model.puntaje_opcion import PuntajeOpcion
from model.persona import Persona
from model.pregunta import Pregunta
from model.test import Test
from model.rango import Rango
from model.ubigeo import Ubigeo
from utils.db import db
from datetime import datetime

puntuaciones = Blueprint('puntuaciones', __name__)

@puntuaciones.route('/puntuaciones/v1', methods=['GET'])
def get_mensaje():
    result = {"data": 'Hola, Puntuaciones'}
    return jsonify(result)

@puntuaciones.route('/puntuaciones/v1/calcular', methods=['POST'])
def calcular_puntuacion_total():
    data = request.json
    id_persona = data['id_persona']
    id_test = data['id_test']

    total_puntaje = db.session.query(db.func.sum(PuntajeOpcion.puntaje)).join(Respuesta, PuntajeOpcion.id_opcion == Respuesta.id_opcion).filter(
        Respuesta.id_persona == id_persona,
        PuntajeOpcion.id_pregunta.in_(db.session.query(Pregunta.id_pregunta).filter(Pregunta.id_test == id_test))
    ).scalar()

    persona = Persona.query.get(id_persona)
    test = Test.query.get(id_test)

    if not persona or not test:
        return jsonify({
            "status_code": 404,
            "msg": "Persona o Test no encontrado"
        }), 404

    # Obtener el rango correspondiente al puntaje total
    rango = Rango.query.filter(Rango.id_test == id_test, Rango.rango_min <= total_puntaje, Rango.rango_max >= total_puntaje).first()

    if not rango:
        interpretacion = "Rango no encontrado"
    else:
        interpretacion = rango.interpretacion

    return jsonify({
        "status_code": 200,
        "msg": "Puntuación total calculada exitosamente",
        "data": {
            "persona": {
                "id_persona": persona.id_persona,
                "apellido_paterno": persona.apellido_paterno,
                "apellido_materno": persona.apellido_materno,
                "nombres": persona.nombres,
                "sexo": persona.sexo,
                "telefono": persona.telefono,
                "fecha_nacimiento": persona.fecha_nacimiento.strftime('%Y-%m-%d')
            },
            "test": {
                "nombre": test.nombre,
                "descripcion": test.descripcion,
                "numero_preguntas": test.numero_preguntas
            },
            "total_puntaje": total_puntaje if total_puntaje else 0,
            "interpretacion": interpretacion
        }
    }), 200

@puntuaciones.route('/puntuaciones/v1/atributos', methods=['POST'])
def obtener_atributos_puntuacion():
    data = request.json
    id_persona = data['id_persona']
    id_test = data['id_test']

    # Obtener la puntuación más reciente para la persona y el test
    puntuacion = Puntuacion.query.filter_by(id_persona=id_persona, id_test=id_test).order_by(Puntuacion.fecha.desc()).first()

    if not puntuacion:
        return jsonify({
            "status_code": 404,
            "msg": "No se encontraron puntuaciones para la persona y test especificados"
        }), 404

    persona = Persona.query.get(id_persona)
    test = Test.query.get(id_test)

    if not persona or not test:
        return jsonify({
            "status_code": 404,
            "msg": "Persona o Test no encontrado"
        }), 404

    rango = Rango.query.get(puntuacion.id_interpretacion)
    interpretacion = rango.interpretacion if rango else "Rango no encontrado"

    return jsonify({
        "status_code": 200,
        "msg": "Atributos de la puntuación recuperados exitosamente",
        "data": {
            "puntaje_total": puntuacion.puntaje_total,
            "nombre": persona.nombres,
            "apellido_paterno": persona.apellido_paterno,
            "apellido_materno": persona.apellido_materno,
            "tipo_test": test.nombre,
            "fecha": puntuacion.fecha.strftime('%Y-%m-%d %H:%M:%S'),
            "calificacion": interpretacion
        }
    }), 200

@puntuaciones.route('/puntuaciones/v1/todos', methods=['GET'])
def obtener_todas_puntuaciones():
    puntuaciones = Puntuacion.query.all()

    if not puntuaciones:
        return jsonify({
            "status_code": 404,
            "msg": "No se encontraron puntuaciones"
        }), 404

    resultado = []

    for puntuacion in puntuaciones:
        persona = Persona.query.get(puntuacion.id_persona)
        test = Test.query.get(puntuacion.id_test)
        ubigeo = Ubigeo.query.get(persona.id_ubigeo)
        rango = Rango.query.get(puntuacion.id_interpretacion)
        calificacion = rango.interpretacion if rango else "Rango no encontrado"

        if not persona or not test or not ubigeo:
            continue

        # Determinar el color según la calificación
        if any(x in calificacion.lower() for x in ["bajo", "baja", "normal"]):
            color = "verde"
        elif any(x in calificacion.lower() for x in ["moderada", "medio"]):
            color = "ambar"
        else:
            color = "rojo"

        resultado.append({
            "id_puntuacion": puntuacion.id_puntuacion,
            "id_persona": puntuacion.id_persona,
            "id_test": puntuacion.id_test,
            "puntaje_total": puntuacion.puntaje_total,
            "nombre": persona.nombres,
            "apellido_paterno": persona.apellido_paterno,
            "apellido_materno": persona.apellido_materno,
            "fecha_nacimiento":persona.fecha_nacimiento,
            "telefono":persona.telefono,
            "sexo":persona.sexo,
            "tipo_test": test.nombre,
            "fecha": puntuacion.fecha.strftime('%Y-%m-%d %H:%M:%S'),
            "calificacion": calificacion,
            "color": color,
            "ubigeo": {
                "id_ubigeo": ubigeo.id_ubigeo,
                "departamento": ubigeo.departamento,
                "provincia": ubigeo.provincia,
                "distrito": ubigeo.distrito,
                "superficie": ubigeo.superficie,
                "poblacion": ubigeo.poblacion,
                "latitud": ubigeo.latitud,
                "longitud": ubigeo.longitud
            }
        })

    return jsonify({
        "status_code": 200,
        "msg": "Puntuaciones recuperadas exitosamente",
        "data": resultado
    }), 200
