from flask import Blueprint, request, jsonify
from model.respuesta import Respuesta
from model.pregunta import Pregunta
from model.persona import Persona
from model.puntaje_opcion import PuntajeOpcion
from model.area import Area
from model.test import Test
from model.rango import Rango
from model.puntuacion import Puntuacion
from utils.db import db
from datetime import datetime

respuestas = Blueprint('respuestas', __name__)

@respuestas.route('/respuestas/v1', methods=['GET'])
def get_mensaje():
    result = {"data": 'Hola, Respuestas'}
    return jsonify(result)

@respuestas.route('/respuestas/v1/listar', methods=['POST'])
def listar_respuestas():
    data = request.json
    id_persona = data.get('id_persona')
    id_test = data.get('id_test')

    respuestas = Respuesta.query.join(PuntajeOpcion, Respuesta.id_opcion == PuntajeOpcion.id_opcion).join(Pregunta, PuntajeOpcion.id_pregunta == Pregunta.id_pregunta).filter(
        Respuesta.id_persona == id_persona,
        Pregunta.id_test == id_test
    ).all()

    if not respuestas:
        return jsonify({
            "status_code": 404,
            "msg": "No se encontraron respuestas para la persona y test especificados"
        }), 404

    result = {
        "respuestas": []
    }

    for respuesta in respuestas:
        puntaje_opcion = PuntajeOpcion.query.get(respuesta.id_opcion)
        pregunta = Pregunta.query.get(puntaje_opcion.id_pregunta)

        respuesta_data = {
            "pregunta": pregunta.texto,
            "respuesta": puntaje_opcion.texto_opcion
        }

        result["respuestas"].append(respuesta_data)

    response = {
        "data": result,
        "status_code": 200,
        "msg": "Se recuperó la lista de preguntas y respuestas"
    }

    return jsonify(response), 200

@respuestas.route('/respuestas/v1/agregar', methods=['POST'])
def agregar_respuestas():
    data = request.json
    id_persona = data.get('id_persona')
    id_test = data.get('id_test')
    respuestas = data.get('respuestas', [])

    if not id_persona or not id_test or not respuestas:
        return jsonify({
            "status_code": 400,
            "msg": "Faltan datos necesarios para agregar las respuestas (id_persona, id_test, respuestas)"
        }), 400

    nuevas_respuestas = []
    for respuesta in respuestas:
        id_pregunta = respuesta.get('id_pregunta')
        texto_respuesta = respuesta.get('texto_respuesta')

        if not id_pregunta or not texto_respuesta:
            return jsonify({
                "status_code": 400,
                "msg": "Cada respuesta debe incluir id_pregunta y texto_respuesta"
            }), 400
    
        # Verificar que la pregunta pertenezca al test
        pregunta = Pregunta.query.get(id_pregunta)
        if not pregunta or pregunta.id_test != id_test:
            return jsonify({
                "status_code": 400,
                "msg": f"La pregunta con id {id_pregunta} no pertenece al test con id {id_test}"
            }), 400

        # Obtener id_opcion basado en el texto de la respuesta
        puntaje_opcion = PuntajeOpcion.query.filter_by(id_pregunta=id_pregunta, texto_opcion=texto_respuesta).first()
        if not puntaje_opcion:
            return jsonify({
                "status_code": 400,
                "msg": f"No se encontró la opción con el texto '{texto_respuesta}' para la pregunta con id {id_pregunta}"
            }), 400

        nueva_respuesta = Respuesta(id_persona=id_persona, id_opcion=puntaje_opcion.id_opcion)
        db.session.add(nueva_respuesta)
        nuevas_respuestas.append(nueva_respuesta)

    db.session.commit()

    # Calcular la puntuación total y guardar en la tabla Puntuacion
    total_puntaje = db.session.query(db.func.sum(PuntajeOpcion.puntaje)).join(Respuesta, PuntajeOpcion.id_opcion == Respuesta.id_opcion).filter(
        Respuesta.id_persona == id_persona,
        PuntajeOpcion.id_pregunta.in_(db.session.query(Pregunta.id_pregunta).filter(Pregunta.id_test == id_test))
    ).scalar()

    rango = Rango.query.filter(Rango.id_test == id_test, Rango.rango_min <= total_puntaje, Rango.rango_max >= total_puntaje).first()

    interpretacion = rango.interpretacion if rango else "Rango no encontrado"

    # Guardar en la tabla Puntuacion
    nueva_puntuacion = Puntuacion(
        puntaje_total=total_puntaje if total_puntaje else 0,
        id_persona=id_persona,
        id_test=id_test,
        fecha=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        id_interpretacion=rango.id_rango if rango else None
    )

    db.session.add(nueva_puntuacion)
    db.session.commit()

    resultado_limpio = []
    for respuesta in nuevas_respuestas:
        respuesta_dict = respuesta.__dict__.copy()
        respuesta_dict.pop('_sa_instance_state', None)
        resultado_limpio.append(respuesta_dict)

    return jsonify({
        "status_code": 201,
        "msg": "Respuestas agregadas exitosamente y puntuación calculada",
        "data": resultado_limpio,
        "total_puntaje": total_puntaje if total_puntaje else 0,
        "interpretacion": interpretacion
    }), 201

@respuestas.route('/respuestas/v1/calcular', methods=['POST'])
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

@respuestas.route('/respuestas/v1/actualizar/<int:id>', methods=['PUT'])
def actualizar_respuesta(id):
    data = request.json
    respuesta = Respuesta.query.get_or_404(id)
    respuesta.id_persona = data.get('id_persona', respuesta.id_persona)
    respuesta.id_opcion = data.get('id_opcion', respuesta.id_opcion)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Respuesta actualizada exitosamente",
        "data": respuesta.__dict__
    }), 200

@respuestas.route('/respuestas/v1/eliminar/<int:id>', methods=['DELETE'])
def eliminar_respuesta(id):
    respuesta = Respuesta.query.get_or_404(id)
    db.session.delete(respuesta)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Respuesta eliminada exitosamente"
    }), 200

@respuestas.route('/respuestas/v1/preguntas/<int:id_test>', methods=['GET'])
def obtener_preguntas_por_test(id_test):
    try:
        preguntas = Pregunta.query.filter_by(id_test=id_test).all()
        if not preguntas:
            return jsonify({
                "status_code": 404,
                "msg": "No se encontraron preguntas para el test especificado"
            }), 404

        preguntas_texto = [{"id_pregunta": pregunta.id_pregunta, "texto": pregunta.texto} for pregunta in preguntas]

        return jsonify({
            "status_code": 200,
            "msg": "Preguntas recuperadas exitosamente",
            "data": preguntas_texto
        }), 200
    except Exception as e:
        return jsonify({
            "status_code": 500,
            "msg": "Error al recuperar preguntas",
            "error": str(e)
        }), 500
