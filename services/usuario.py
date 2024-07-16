from flask import Blueprint, request, jsonify
import pytz
from werkzeug.security import generate_password_hash, check_password_hash
from model.usuario import Usuario
from model.rol import Rol
from model.usuario_rol import UsuarioRol
from model.conversacion import Conversacion
from utils.db import db
import google.generativeai as genai
import PIL.Image
from model.persona import Persona
from model.ubigeo import Ubigeo
from datetime import datetime
from pytz import timezone
import os

usuarios = Blueprint('usuarios', __name__)

# Configura tu API key de Google Gemini
genai.configure(api_key="AIzaSyBsX1cBYxC0FyESuPbRx9Oj9bwTgDIrR1Q")  

# Directorio para guardar las imágenes cargadas
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Particiones del contexto inicial
contexto_dict = {
    "rol": "Eres SanMarBot, un asistente virtual que también puede procesar imágenes, diseñado para ayudar a los estudiantes de la Universidad Nacional Mayor de San Marcos (UNMSM) en Perú a manejar el estrés, la ansiedad y la depresión relacionadas a situaciones académicas.",
    
    "tarea": "Proporcionas respuestas empáticas, consejos prácticos, técnicas de relajación e interpretación de imágenes brindadas por el usuario, ayudas en preguntas especificas academicaas, respecto al tema estudiantil.",
    
    "contexto": """
Entiendes las dificultades que enfrentan los estudiantes, como la presión de los exámenes, la carga de trabajo y las expectativas académicas. Ofreces muy buenas estrategias efectivas para el manejo del tiempo, la organización de estudios y el autocuidado. Además brindas la información necesaria de entidades, temas especificos de cursos, o del mismo usuario si es que este lo pide.
""",
    
    "tono": "Siempre hablas con un tono amable, comprensivo y tranquilizador.",
    
    "informacion_usuario": """
### Información del Usuario:

- Nombre: {nombres} {apellido_paterno} {apellido_materno}
- Sexo: {sexo}
- Teléfono: {telefono}
- Fecha de Nacimiento: {fecha_nacimiento}
""",
    
    "ejemplos": """
### Ejemplos de Conversaciones:

1. *Usuario:* "Estoy muy estresado por los exámenes finales."
   *SanMarBot:* "Entiendo que los exámenes finales pueden ser muy estresantes. ¿Te gustaría probar una técnica de respiración profunda para relajarte? Inhala contando hasta cuatro, mantén el aire durante cuatro segundos y exhala lentamente contando hasta seis. Repite esto unas cuantas veces y dime cómo te sientes."

2. *Usuario:* "No puedo concentrarme en mis estudios."
   *SanMarBot:* "Es difícil concentrarse cuando estás estresado. Intenta establecer bloques de estudio de 25 minutos seguidos de un descanso de 5 minutos. Esta técnica, llamada Pomodoro, puede ayudarte a mantener la concentración. ¿Te gustaría intentarlo?"

3. *Usuario:* "Me siento muy ansioso y no sé cómo manejarlo."
   *SanMarBot:* "Siento mucho que te sientas ansioso. Una cosa que puede ayudar es practicar la atención plena. Intenta sentarte en un lugar tranquilo, cierra los ojos y enfócate en tu respiración. Observa cómo entra y sale el aire de tus pulmones. Si tu mente se distrae, gentilmente redirígela a tu respiración. Practicar esto unos minutos al día puede reducir la ansiedad."

4. *Usuario:* "Estoy deprimido y no tengo motivación para estudiar."
   *SanMarBot:* "Lo siento mucho. Recuerda que está bien pedir ayuda cuando la necesitas. Hablar con un consejero o un amigo de confianza puede hacer una gran diferencia. También, intenta establecer pequeñas metas alcanzables para tus estudios. A veces, dar pequeños pasos puede ayudarte a recuperar la motivación."

5. *Usuario:* "Quiero que me proporciones mis datos."
   *SanMarBot:* "Claro, tus datos son que te llamas Miguel Ángel Huere Sánchez, tu edad es 23, y tu sexo es masculino. ¿Alguna duda acerca de tus estudios?"
""",
   
    "recursos": """
### Recursos Adicionales:

- *Líneas de Ayuda y Consejería*: Proporciona información sobre los servicios de consejería de la universidad y líneas de ayuda para estudiantes.
- *Técnicas de Estudio y Manejo del Tiempo*: Sugerencias y recursos sobre técnicas efectivas de estudio y cómo organizar el tiempo de manera productiva.
- *Ejercicios de Relajación y Atención Plena*: Instrucciones para ejercicios de respiración, meditación y atención plena que pueden ayudar a reducir el estrés y la ansiedad.
- *Recomendacion de cursos , ejercicios , temas para practicar respecto al curso que se le presenta dificultad al estudiante.
""",
    
    "formato": """
Recuerda, SanMarBot, siempre mantén un tono amable ,tranquilizador, motivador, y asegúrate de validar los sentimientos de los estudiantes mientras ofreces consejos prácticos y apoyo emocional. No olvides que no saludes a cada rato por cada consulta, solo saluda cuando el mensaje que te mandan es de saludo.
"""
}

# Juntar todas las partes en un solo string
contexto_inicial = f"""
{contexto_dict["rol"]}

{contexto_dict["tarea"]}

{contexto_dict["contexto"]}

{contexto_dict["tono"]}

{contexto_dict["informacion_usuario"]}

{contexto_dict["ejemplos"]}

{contexto_dict["recursos"]}

{contexto_dict["formato"]}
"""



@usuarios.route('/usuarios/v1', methods=['GET'])
def get_mensaje():
    result = {"data": 'Hola, Usuarios'}
    return jsonify(result)

@usuarios.route('/usuarios/v1/login/paciente', methods=['POST'])
def login_paciente():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    usuario = Usuario.query.filter_by(username=username).first()
    if usuario and check_password_hash(usuario.password, password):
        usuario_rol = UsuarioRol.query.filter_by(id_usuario=usuario.id_usuario).first()
        rol = Rol.query.get(usuario_rol.id_rol)
        if rol.tipo_rol == 'Paciente':
            persona = Persona.query.get(usuario.id_persona)
            return jsonify({
                "status_code": 200,
                "msg": "Login successful",
                "data": {
                    "id_usuario": usuario.id_usuario,
                    "username": usuario.username,
                    "id_persona": usuario.id_persona,
                    "rol": rol.tipo_rol,
                    "persona": {
                        "id_persona": persona.id_persona,
                        "apellido_paterno": persona.apellido_paterno,
                        "apellido_materno": persona.apellido_materno,
                        "nombres": persona.nombres,
                        "sexo": persona.sexo,
                        "telefono": persona.telefono,
                        "fecha_nacimiento": persona.fecha_nacimiento.strftime('%Y-%m-%d')
                    }
                }
            }), 200
        else:
            return jsonify({
                "status_code": 403,
                "msg": "Unauthorized role"
            }), 403
    else:
        return jsonify({
            "status_code": 401,
            "msg": "Invalid credentials"
        }), 401

@usuarios.route('/usuarios/v1/login/especialista', methods=['POST'])
def login_especialista():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    usuario = Usuario.query.filter_by(username=username).first()
    if usuario and check_password_hash(usuario.password, password):
        usuario_rol = UsuarioRol.query.filter_by(id_usuario=usuario.id_usuario).first()
        rol = Rol.query.get(usuario_rol.id_rol)
        if rol.tipo_rol == 'Especialista':
            persona = Persona.query.get(usuario.id_persona)
            ubigeo = Ubigeo.query.get(persona.id_ubigeo)  # Assuming you have a foreign key relationship

            return jsonify({
                "status_code": 200,
                "msg": "Login successful",
                "data": {
                    "id_usuario": usuario.id_usuario,
                    "username": usuario.username,
                    "id_persona": usuario.id_persona,
                    "rol": rol.tipo_rol
                },
                "personaData": {
                    "nombres": persona.nombres,
                    "apellido_paterno": persona.apellido_paterno,
                    "apellido_materno": persona.apellido_materno,
                    "sexo": persona.sexo,
                    "telefono": persona.telefono,
                    "departamento": ubigeo.departamento,
                    "provincia": ubigeo.provincia,
                    "distrito": ubigeo.distrito
                }
            }), 200
        else:
            return jsonify({
                "status_code": 403,
                "msg": "Unauthorized role"
            }), 403
    else:
        return jsonify({
            "status_code": 401,
            "msg": "Invalid credentials"
        }), 401

@usuarios.route('/usuarios/v1/agregar', methods=['POST'])
def agregar_usuario():
    data = request.json
    username = data['username']
    password = data['password']
    id_persona = data['id_persona']
    rol_tipo = data['rol']

    # Verificar si el username ya existe
    if Usuario.query.filter_by(username=username).first():
        return jsonify({
            "status_code": 400,
            "msg": "El nombre de usuario ya existe"
        }), 400

    # Crear nuevo usuario
    nuevo_usuario = Usuario(
        username=username,
        password=password,  # La contraseña se hashea en el constructor del modelo
        id_persona=id_persona
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    # Asignar rol
    rol = Rol.query.filter_by(tipo_rol=rol_tipo).first()
    if not rol:
        return jsonify({
            "status_code": 400,
            "msg": "Rol no válido"
        }), 400

    nuevo_usuario_rol = UsuarioRol(id_usuario=nuevo_usuario.id_usuario, id_rol=rol.id_rol)
    db.session.add(nuevo_usuario_rol)
    db.session.commit()

    # Preparar datos serializables
    usuario_data = {
        "id_usuario": nuevo_usuario.id_usuario,
        "username": nuevo_usuario.username,
        "id_persona": nuevo_usuario.id_persona
    }

    return jsonify({
        "status_code": 201,
        "msg": "Usuario agregado exitosamente",
        "data": usuario_data
    }), 201

@usuarios.route('/usuarios/v1/actualizar/<int:id>', methods=['PUT'])
def actualizar_usuario(id):
    data = request.json
    usuario = Usuario.query.get_or_404(id)
    usuario.username = data.get('username', usuario.username)
    usuario.password = data.get('password', usuario.password)
    usuario.id_persona = data.get('id_persona', usuario.id_persona)
    db.session.commit()

    # Actualizar rol
    if 'rol' in data:
        rol = Rol.query.filter_by(tipo_rol=data['rol']).first()
        if not rol:
            return jsonify({
                "status_code": 400,
                "msg": "Rol no válido"
            }), 400
        usuario_rol = UsuarioRol.query.filter_by(id_usuario=usuario.id_usuario).first()
        usuario_rol.id_rol = rol.id_rol
        db.session.commit()

    return jsonify({
        "status_code": 200,
        "msg": "Usuario actualizado exitosamente",
        "data": usuario.__dict__
    }), 200

@usuarios.route('/usuarios/v1/eliminar/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({
        "status_code": 200,
        "msg": "Usuario eliminado exitosamente"
    }), 200

@usuarios.route('/usuarios/v1/correo/<int:id_persona>', methods=['GET'])
def obtener_correo(id_persona):
    persona = Persona.query.get(id_persona)
    if persona:
        usuario = Usuario.query.filter_by(id_persona=persona.id_persona).first()
        if usuario:
            return jsonify({"status_code": 200, "data": {"correo": usuario.username}}), 200  # Suponiendo que el username es el correo
    return jsonify({"status_code": 404, "msg": "Correo no encontrado para la persona dada"}), 404

@usuarios.route('/usuarios/v1/listar', methods=['GET'])
def listar_usuarios():
    usuarios = Usuario.query.all()
    result = {
        "data": [usuario.__dict__ for usuario in usuarios],
        "status_code": 200,
        "msg": "Se recuperó la lista de Usuarios sin inconvenientes"
    }
    for usuario in result["data"]:
        usuario.pop('_sa_instance_state', None)  # Eliminar metadata de SQLAlchemy
    return jsonify(result), 200

@usuarios.route('/registrar-persona-usuario', methods=['POST'])
def registrar_persona_usuario():
    data = request.json
    print('Datos recibidos:', data)

    # Verificar si el username ya existe
    usuario_existente = Usuario.query.filter_by(username=data['username']).first()
    if usuario_existente:
        print('Usuario existente:', usuario_existente)
        return jsonify({
            "status_code": 400,
            "msg": "El nombre de usuario ya existe"
        }), 400

    # Registrar Persona
    nueva_persona = Persona(
        apellido_paterno=data['apellidoPaterno'],
        apellido_materno=data['apellidoMaterno'],
        nombres=data['nombres'],
        sexo=data['sexo'],
        telefono=data['telefono'],
        fecha_nacimiento=data['fechaNacimiento'],
        id_ubigeo=data['ubigeo']
    )
    db.session.add(nueva_persona)
    db.session.commit()

    # Usar el id de la persona recién creada
    id_persona = nueva_persona.id_persona
    print('Persona registrada:', nueva_persona)

    # Registrar Usuario
    nuevo_usuario = Usuario(
        username=data['username'],
        password=data['password'],  # La contraseña se hashea en el constructor del modelo
        id_persona=id_persona
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    print('Usuario registrado:', nuevo_usuario)

    # Asignar rol
    rol = Rol.query.filter_by(tipo_rol=data['rol']).first()
    if not rol:
        print('Rol no encontrado:', data['rol'])
        return jsonify({
            "status_code": 400,
            "msg": "Rol no válido"
        }), 400

    nuevo_usuario_rol = UsuarioRol(id_usuario=nuevo_usuario.id_usuario, id_rol=rol.id_rol)
    db.session.add(nuevo_usuario_rol)
    db.session.commit()
    print('Rol asignado:', nuevo_usuario_rol)

    # Preparar datos serializables
    usuario_data = {
        "id_usuario": nuevo_usuario.id_usuario,
        "username": nuevo_usuario.username,
        "id_persona": nuevo_usuario.id_persona
    }

    return jsonify({
        "status_code": 201,
        "msg": "Usuario agregado exitosamente",
        "data": usuario_data
    }), 201

# Función para generar el título
def generar_titulo(pregunta_usuario):
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        prompt = f"Genera solamente un título SOLO UNO breve , solo dme esa respuesta ,para la siguiente consulta:\nPregunta: {pregunta_usuario}\nTítulo:"
        response = model.generate_content([prompt])
        titulo = response.text.strip()
        if not titulo:
            raise ValueError("El título generado es vacío.")
        return titulo
    except Exception as e:
        print(f"Error al generar el título: {e}")
        return None

@usuarios.route('/usuarios/v1/generar_titulo', methods=['POST'])
def generar_titulo_endpoint():
    data = request.get_json()
    pregunta_usuario = data.get('pregunta')

    if not pregunta_usuario:
        return jsonify({"error": "No se proporcionó ninguna pregunta"}), 400

    titulo = generar_titulo(pregunta_usuario)
    if not titulo:
        return jsonify({"error": "No se pudo generar el título"}), 500
    
    return jsonify({'titulo': titulo}), 200
@usuarios.route('/usuarios/v1/chatbot', methods=['POST'])
def chatbot():
    username = request.form.get('username')
    pregunta_usuario = request.form.get('pregunta')
    image = request.files.get('image')

    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if not pregunta_usuario:
        return jsonify({"error": "No se proporcionó ninguna pregunta"}), 400

    # Guardar la imagen si se proporciona
    img_path = None
    if image:
        img_filename = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(img_filename)
        img_path = img_filename

    # Obtener datos del usuario
    persona = Persona.query.get(usuario.id_persona)

    # Generar el título de la conversación
    titulo = generar_titulo(pregunta_usuario)
    if not titulo:
        return jsonify({"error": "No se pudo generar el título de la conversación"}), 500

    # Buscar una conversación existente del mismo usuario y título
    conversacion = Conversacion.query.filter_by(id_usuario=usuario.id_usuario, titulo=titulo).first()

    # Si no existe, crear una nueva conversación
    if not conversacion:
        conversacion = Conversacion(id_usuario=usuario.id_usuario, titulo=titulo, contenido="")
    else:
        # Si existe, agregar la nueva pregunta al contenido
        conversacion.contenido += f"\nPregunta: {pregunta_usuario}\nRespuesta:"

    # Personalizar el contexto inicial con los datos del usuario
    contexto_personalizado = contexto_inicial.format(
        nombres=persona.nombres,
        apellido_paterno=persona.apellido_paterno,
        apellido_materno=persona.apellido_materno,
        sexo=persona.sexo,
        telefono=persona.telefono,
        fecha_nacimiento=persona.fecha_nacimiento.strftime('%Y-%m-%d')
    )

    # Combinamos el contexto personalizado con la pregunta del usuario
    prompt = f"{contexto_personalizado}\nPregunta: {pregunta_usuario}\nRespuesta:"

    try:
        # Genera el contenido utilizando la API de Gemini
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        if img_path:
            img = PIL.Image.open(img_path)
            response = model.generate_content([prompt, img])
        else:
            response = model.generate_content([prompt])
        # Extrae la respuesta generada
        respuesta = response.text.strip().replace('*', '')  # Eliminar los asteriscos
    except Exception as e:
        print(f"Error al generar la respuesta: {e}")
        return jsonify({"error": "No se pudo generar la respuesta a la pregunta"}), 500

    # Acumular la conversación en el contenido
    conversacion.contenido += f"\nPregunta: {pregunta_usuario}\nRespuesta: {respuesta}"
    
    # Ajuste para la zona horaria de Perú
    tz = pytz.timezone('America/Lima')
    ahora = datetime.now(tz)
    conversacion.fecha = ahora.date()
    conversacion.hora = ahora.time()

    try:
        # Guardar la conversación en la base de datos
        db.session.add(conversacion)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error al guardar la conversación: {e}")
        return jsonify({"error": "Error al guardar la conversación en la base de datos"}), 500

    return jsonify({'respuesta': respuesta, 'conversacion_id': conversacion.id, 'titulo': titulo})

@usuarios.route('/usuarios/v1/seguir_conversacion', methods=['POST'])
def seguir_conversacion():
    username = request.form.get('username')
    titulo = request.form.get('titulo')
    pregunta_usuario = request.form.get('pregunta')
    image = request.files.get('image')

    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    conversacion = Conversacion.query.filter_by(id_usuario=usuario.id_usuario, titulo=titulo).first()
    if not conversacion:
        return jsonify({"error": "Conversación no encontrada"}), 404

    # Guardar la imagen si se proporciona
    img_path = None
    if image:
        img_filename = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(img_filename)
        img_path = img_filename

    # Obtener datos del usuario
    persona = Persona.query.get(usuario.id_persona)

    # Personalizar el contexto inicial con los datos del usuario
    contexto_personalizado = contexto_inicial.format(
        nombres=persona.nombres,
        apellido_paterno=persona.apellido_paterno,
        apellido_materno=persona.apellido_materno,
        sexo=persona.sexo,
        telefono=persona.telefono,
        fecha_nacimiento=persona.fecha_nacimiento.strftime('%Y-%m-%d')
    )

    # Combinamos el contexto personalizado con la pregunta del usuario y el contenido acumulado
    prompt = f"{contexto_personalizado}\n{conversacion.contenido}\nPregunta: {pregunta_usuario}\nRespuesta:"

    try:
        # Genera el contenido utilizando la API de Gemini
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        if img_path:
            img = PIL.Image.open(img_path)
            response = model.generate_content([prompt, img])
        else:
            response = model.generate_content([prompt])
        # Extrae la respuesta generada
        respuesta = response.text.strip().replace('*', '')  # Eliminar los asteriscos
    except Exception as e:
        print(f"Error al generar la respuesta: {e}")
        return jsonify({"error": "No se pudo generar la respuesta a la pregunta"}), 500

    # Acumular la nueva pregunta y respuesta en el contenido
    conversacion.contenido += f"\nPregunta: {pregunta_usuario}\nRespuesta: {respuesta}"
    
    # Actualizar la fecha y hora de la última interacción
    tz = pytz.timezone('America/Lima')
    ahora = datetime.now(tz)
    conversacion.fecha = ahora.date()
    conversacion.hora = ahora.time()

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error al guardar la conversación: {e}")
        return jsonify({"error": "Error al guardar la conversación en la base de datos"}), 500

    return jsonify({'respuesta': respuesta, 'conversacion_id': conversacion.id, 'titulo': titulo})

# Lista de títulos de conversaciones por usuario
@usuarios.route('/usuarios/v1/listar_conversaciones', methods=['POST'])
def listar_conversaciones():
    data = request.get_json()
    username = data.get('username')
    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario:
        return jsonify({"status_code": 404, "msg": "Usuario no encontrado"}), 404

    conversaciones = Conversacion.query.filter_by(id_usuario=usuario.id_usuario).all()
    result = [
        {"titulo": conversacion.titulo} for conversacion in conversaciones
    ]

    return jsonify({"status_code": 200, "data": result}), 200

@usuarios.route('/usuarios/v1/obtener_conversacion', methods=['POST'])
def obtener_conversacion():
    data = request.get_json()
    username = data.get('username')
    titulo = data.get('titulo')
    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario:
        return jsonify({"status_code": 404, "msg": "Usuario no encontrado"}), 404

    conversacion = Conversacion.query.filter_by(id_usuario=usuario.id_usuario, titulo=titulo).first()
    if not conversacion:
        return jsonify({"status_code": 404, "msg": "Conversación no encontrada"}), 404

    # Asumir que el contenido sigue el formato:
    # "Pregunta: <pregunta>\nRespuesta: <respuesta>"
    mensajes = conversacion.contenido.split('\n')
    messages = []
    current_message = {}
    for mensaje in mensajes:
        if mensaje.startswith("Pregunta:"):
            if current_message:
                messages.append(current_message)
            current_message = {"text": mensaje.replace("Pregunta: ", ""), "isUser": True}
        elif mensaje.startswith("Respuesta:"):
            if current_message:
                messages.append(current_message)
            current_message = {"text": mensaje.replace("Respuesta: ", ""), "isUser": False}
        else:
            if current_message and not current_message.get("isUser", True):
                current_message["text"] += f"\n{mensaje}"
    if current_message:
        messages.append(current_message)

    return jsonify({"status_code": 200, "data": {"messages": messages}}), 200


@usuarios.route('/usuarios/v1/eliminar_conversacion', methods=['DELETE'])
def eliminar_conversacion():
    data = request.get_json()
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
