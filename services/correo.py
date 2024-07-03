from flask import Blueprint, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from werkzeug.utils import secure_filename
from model.persona import Persona
from model.usuario import Usuario
import os

correos = Blueprint('correos', __name__)
CORS(correos, resources={r"/*": {"origins": "*"}})

@correos.route('/enviar-correo', methods=['POST'])
def enviar_correo():
    if 'pdf' not in request.files:
        return jsonify({"status_code": 400, "msg": "No se encontró el archivo PDF adjunto"}), 400

    id_persona = request.form['id_persona']
    asunto = request.form['asunto']
    pdf_file = request.files['pdf']

    # Guardar el archivo PDF en un directorio temporal
    filename = secure_filename(pdf_file.filename)
    temp_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    pdf_path = os.path.join(temp_dir, filename)
    pdf_file.save(pdf_path)

    # Obtener el correo del usuario
    correo_persona = obtener_correo_persona(id_persona)

    if not correo_persona:
        return jsonify({"status_code": 400, "msg": "Correo no encontrado para la persona dada"}), 400

    destinatario = correo_persona

   
    remitente = "sisvitaunmsm@gmail.com" 
    password = "dczyqwmlengetqkt"  

    try:
        msg = MIMEMultipart()
        msg['Subject'] = asunto
        msg['From'] = remitente
        msg['To'] = destinatario

        # Adjuntar el archivo PDF
        with open(pdf_path, "rb") as f:
            attach = MIMEApplication(f.read(), _subtype="pdf")
            attach.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(attach)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(remitente, password)
            server.sendmail(remitente, destinatario, msg.as_string())

        return jsonify({"status_code": 200, "msg": "Correo enviado exitosamente"}), 200

    except Exception as e:
        return jsonify({"status_code": 500, "msg": str(e)}), 500

def obtener_correo_persona(id_persona):
    persona = Persona.query.get(id_persona)
    if persona:
        usuario = Usuario.query.filter_by(id_persona=persona.id_persona).first()
        if usuario:
            return usuario.username  
    return None
