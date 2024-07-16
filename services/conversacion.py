# services/conversaciones.py
from flask import Blueprint, request, jsonify
from model.conversacion import Conversacion
from model.usuario import Usuario
from utils.db import db
import google.generativeai as genai
import PIL.Image
from datetime import datetime
from pytz import timezone

conversaciones = Blueprint('conversaciones', __name__)

# Configura tu API key de Google Gemini
genai.configure(api_key="AIzaSyBsX1cBYxC0FyESuPbRx9Oj9bwTgDIrR1Q")

# Define un contexto inicial sobre la historia del Perú republicano
contexto_inicial = """
Eres un experto en aconsejar y dar recomendaciones sobre la ansiedad en jóvenes 
universitarios y además puedes recomendar libros de ayuda para diferentes tipos de ansiedad que presentan.
Incluido que puedes planificar o planificar mejor un buen horario solo con entrar el pdf de los horarios, 
de un texto ingresado sobre dicha información o imágenes de este mismo. Muestra emojis, se amigable y muestra gran empatía.
"""

# Función para generar el título de la conversación
def generar_titulo(pregunta):
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    prompt = f"Genera un título breve para la siguiente consulta:\nPregunta: {pregunta}\nTítulo:"
    response = model.generate_content([prompt])
    titulo = response.text.strip()
    return titulo

@conversaciones.route('/conversaciones/v1', methods=['GET'])
def get_mensaje():
    result = {"data": 'Hola, Conversaciones'}
    return jsonify(result)

@conversaciones.route('/conversaciones/v1/listar/<string:username>', methods=['GET'])
def listar_conversaciones(username):
    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    conversas = Conversacion.query.filter_by(id_usuario=usuario.id_usuario).all()
    result = {
        "data": [conversa.__dict__ for conversa in conversas],
        "status_code": 200,
        "msg": "Se recuperó la lista de Conversaciones sin inconvenientes"
    }
    for conversa in result["data"]:
        conversa.pop('_sa_instance_state', None)  # Eliminar metadata de SQLAlchemy
    return jsonify(result), 200

@conversaciones.route('/conversaciones/v1/agregar', methods=['POST'])
def agregar_conversacion():
    data = request.json
    username = data['username']
    pregunta_usuario = data['pregunta']

    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Generar el título de la conversación
    titulo = generar_titulo(pregunta_usuario)

    # Buscar una conversación existente del mismo usuario y título
    conversacion = Conversacion.query.filter_by(id_usuario=usuario.id_usuario, titulo=titulo).first()

    # Si no existe, crear una nueva conversación
    if not conversacion:
        conversacion = Conversacion(id_usuario=usuario.id_usuario, titulo=titulo, contenido="")

    # Combinamos el contexto inicial con la pregunta del usuario
    prompt = f"{conversacion.contenido}\nPregunta: {pregunta_usuario}\nRespuesta:"

    # Genera el contenido utilizando la API de Gemini
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    response = model.generate_content([prompt])

    # Extrae la respuesta generada
    respuesta = response.text

    # Acumular la conversación en el contenido
    conversacion.contenido += f"\nPregunta: {pregunta_usuario}\nRespuesta: {respuesta}"

    # Ajuste para la zona horaria de Perú
    tz = timezone('America/Lima')
    ahora = datetime.now(tz)
    conversacion.fecha = ahora.date()
    conversacion.hora = ahora.time()

    # Guardar la conversación en la base de datos
    db.session.add(conversacion)
    db.session.commit()

    return jsonify({'respuesta': respuesta, 'conversacion_id': conversacion.id, 'titulo': titulo})

@conversaciones.route('/conversaciones/v1/actualizar/<int:id>', methods=['PUT'])
def actualizar_conversacion(id):
    data = request.json
    conversacion = Conversacion.query.get_or_404(id)
    conversacion.titulo = data.get('titulo', conversacion.titulo)
    conversacion.contenido = data.get('contenido', conversacion.contenido)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Conversación actualizada exitosamente",
        "data": conversacion.__dict__
    }), 200

@conversaciones.route('/conversaciones/v1/eliminar', methods=['DELETE'])
def eliminar_conversacion():
    data = request.json
    username = data.get('username')
    titulo = data.get('titulo', None)

    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Eliminar las conversaciones del usuario
    if titulo:
        Conversacion.query.filter_by(id_usuario=usuario.id_usuario, titulo=titulo).delete()
    else:
        Conversacion.query.filter_by(id_usuario=usuario.id_usuario).delete()

    db.session.commit()

    return jsonify({"msg": "Conversación(es) eliminada(s) exitosamente"}), 200
