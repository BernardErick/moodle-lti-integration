from flask import Blueprint, request, jsonify, render_template, redirect, send_file
import os
import urllib.parse
import json
import qrcode
import io
import base64
from PIL import Image

# Criando um blueprint para facilitar a organização de rotas na aplicação!
main = Blueprint('main', __name__)

# Rota inicial para receber as requisições POST do Moodle LTI
@main.route('/lti-receiver', methods=['POST'])
def lti_receiver():
    lti_data = request.form.to_dict()
    print("Dados LTI recebidos primeira vez:", lti_data)
    return redirect('/print-qrcode', code=307)

# Rota para exibir dados e gerar QR Code
@main.route('/print-qrcode', methods=['POST', 'GET'])
def print_data():
    lti_data = request.form.to_dict()
    print("Dados LTI recebidos segunda vez:", lti_data)


    # Dados LTI simulados
    lti_data = {
        "oauth_consumer_key": str(lti_data.get('oauth_consumer_key', 'N/A')), #Chave do consumidor
        "user_id": str(lti_data.get('user_id', 'N/A')), #Id do usuario no moodle
        "context_id": str(lti_data.get('context_id', 'N/A')), #Id da disciplina/curso no moodle
        "context_title": str(lti_data.get('context_title', 'N/A')), #Nome da disciplina/curso
        "lis_person_name_full": str(lti_data.get('lis_person_name_full', 'N/A')), #Nome completo do usuario
        "ext_user_username": str(lti_data.get('ext_user_username', 'N/A')), #Username/Matricula do usuario
        "lis_person_contact_email_primary": str(lti_data.get('lis_person_contact_email_primary', 'N/A')), #Email do usuario
        "context_label": str(lti_data.get('context_label', 'N/A')), #Nome breve da disciplina
        "roles": str(lti_data.get('roles', 'N/A'))
    }
    

    qr_data = generate_qr_data(lti_data)
    img_base64 = create_qr_image(qr_data)

    return render_template('qr_code.html', img_base64=img_base64)

@main.route('/receive-lti-data', methods=['GET'])
def receive_lti_data():
    # Recuperar dados LTI da URL
    lti_data_encoded = request.args.get('data')
    if not lti_data_encoded:
        return jsonify({"error": "Dados LTI não fornecidos"}), 400

    # Decodificar e carregar os dados LTI
    lti_data_json = urllib.parse.unquote(lti_data_encoded)
    lti_data = json.loads(lti_data_json)

    # Print dos dados recebidos no console
    print("Dados LTI recebidos:", lti_data)

    # Extrair 6 campos para o painel (você pode ajustar conforme necessário)
    campos = {
        "oauth_consumer_key": lti_data.get('oauth_consumer_key', 'N/A'), #Chave do consumidor
        "user_id": lti_data.get('user_id', 'N/A'), #Id do usuario no moodle
        "context_id": lti_data.get('context_id', 'N/A'), #Id da disciplina/curso no moodle
        "context_title": lti_data.get('context_title', 'N/A'), #Nome da disciplina/curso
        "lis_person_name_full": lti_data.get('lis_person_name_full', 'N/A'), #Nome completo do usuario
        "ext_user_username": lti_data.get('ext_user_username', 'N/A'), #Username/Matricula do usuario
        "lis_person_contact_email_primary": lti_data.get('lis_person_contact_email_primary', 'N/A'), #Email do usuario
        "context_label": lti_data.get('context_label', 'N/A'), #Nome breve da disciplina
        "roles": lti_data.get('roles', 'N/A')
    }

    # Renderizar o template passando os dados
    return render_template('painel.html', campos=campos), 200

# Rota para retornar a imagem
@main.route('/get-image', methods=['GET'])
def get_image():
    image_path = os.path.join(os.getcwd(), 'img/logo.png')
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/jpeg')
    return jsonify({"error": "Imagem não encontrada"}), 404

# Importando funções auxiliares do arquivo utils
from .utils import generate_qr_data, create_qr_image
