from flask import Flask, request, jsonify, send_file, render_template_string, redirect
import os
import qrcode
import io
import urllib.parse
import json
import base64
from PIL import Image, ImageDraw  # Importando as bibliotecas necessárias do Pillow

app = Flask(__name__)


# Endpoint inicial para receber as requisições POST do Moodle LTI
@app.route('/lti-receiver', methods=['POST'])
def lti_receiver():
    lti_data = request.form.to_dict()  # Dados recebidos do Moodle LTI
    print("Dados LTI recebidos primeira vez:", lti_data)
    
    # Redireciona para o segundo endpoint com status 307 (mantém o método POST)
    return redirect('/print-qrcode', code=307)

# Endpoint secundário para exibir os dados recebidos e gerar o QR Code
@app.route('/print-qrcode', methods=['POST', 'GET'])
def print_data():
    lti_data = request.form.to_dict()

    # Exibe os dados no console
    print("Dados LTI recebidos segunda vez:", lti_data)

    user_id = lti_data.get("user_id")
    resource_link_title = lti_data.get("resource_link_title")
    oauth_consumer_key = lti_data.get("oauth_consumer_key")
    lis_person_contact_email_primary = lti_data.get("lis_person_contact_email_primary")
    ext_user_username = lti_data.get("ext_user_username")

    # Dados LTI simulados
    lti_data = {
        "user_id": str(user_id),
        "resource_link_title": str(resource_link_title),
        "oauth_consumer_key": str(oauth_consumer_key),
        "lis_person_contact_email_primary": str(lis_person_contact_email_primary),
        "ext_user_username": str(ext_user_username)
    }

    # Cria a URL do POST que será embutida no QR Code
    post_url = "http://localhost:5000/receive-lti-data"
    
    # Serializa os dados em JSON para passar no corpo do POST
    lti_data_json = json.dumps(lti_data)

    # Codifica os dados JSON na URL
    encoded_data = urllib.parse.quote(lti_data_json)

    # Gera o QR Code com a URL e dados LTI codificados
    qr_data = f"{post_url}?data={encoded_data}"

    # Forçar uma versão menor do QR Code (por exemplo, versão 10)
    qr = qrcode.QRCode(
        version=10,  # Ajuste a versão conforme necessário (1 a 40)
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Cria um buffer para enviar o QR Code como imagem
    img = io.BytesIO()

    # Cria a imagem do QR Code com o fundo branco e código preto
    qr_img = qr.make_image(fill='black', back_color='white')

    # Converte a imagem do QR Code para RGB (para garantir que tenha o mesmo modo que a imagem de fundo)
    qr_img_rgb = qr_img.convert('RGB')

    # Agora vamos criar uma nova imagem com o fundo colorido e o QR Code no meio
    width, height = qr_img_rgb.size
    background_color = '#3c7593'  # Cor de fundo ao redor do QR Code

    # Criar uma nova imagem maior, com o fundo colorido
    new_img = Image.new('RGB', (width + 40, height + 40), background_color)  # Adicionando uma borda de 20px em cada lado

    # Colar a imagem do QR Code no centro da nova imagem
    new_img.paste(qr_img_rgb, (20, 20))

    # Salva a imagem com o fundo colorido
    new_img.save(img, format='PNG')
    img.seek(0)

    # Converte a imagem para base64 para exibir no HTML
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    # Exibe o QR Code em um template HTML com a centralização
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>QR Code</title>
            <style>
                body {
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f0f0f0;
                    font-family: Arial, sans-serif;
                    color: #3c7593;
                    text-align: center;
                }
                h3 {
                    font-size: 2rem;
                    font-weight: bold;
                    color: #3c7593;
                    margin-bottom: 10px;
                }
                p {
                    font-size: 1.2rem;
                    font-weight: bold;
                    color: #3c7593;
                    margin-bottom: 20px;
                }
                img {
                    max-width: 90%;
                    height: auto;
                    border-radius: 20px;
                    margin-top: 20px;
                    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1); /* Adiciona sombra ao QR Code */
                }
            </style>
        </head>
        <body>
            <header>
                <h3>Entre nessa jornada da TrilhaEdu! ❤️</h3>
            </header>
            <main>
                <p>Use a câmera 📷 do seu aplicativo mobile para escanear o QR Code abaixo e faça parte dessa trilha!</p>
                <img src="data:image/png;base64,{{ img_base64 }}" alt="QR Code">
            </main>
        </body>
        </html>
    """, img_base64=img_base64)

# Endpoint para receber os dados LTI passados via GET e processá-los
@app.route('/receive-lti-data', methods=['GET'])
def receive_lti_data():
    # Extrai os dados LTI passados na URL como parâmetro 'data'
    lti_data_encoded = request.args.get('data')
    
    if not lti_data_encoded:
        return jsonify({"error": "Dados LTI não fornecidos"}), 400

    # Decodifica os dados LTI codificados
    lti_data_json = urllib.parse.unquote(lti_data_encoded)
    lti_data = json.loads(lti_data_json)

    # Imprime os dados LTI no console
    print("Dados LTI recebidos:")
    print(f"user_id: {lti_data.get('user_id')}")
    print(f"resource_link_title: {lti_data.get('resource_link_title')}")
    print(f"oauth_consumer_key: {lti_data.get('oauth_consumer_key')}")
    print(f"lis_person_contact_email_primary: {lti_data.get('lis_person_contact_email_primary')}")
    print(f"ext_user_username: {lti_data.get('ext_user_username')}")

    # Retorna uma resposta JSON confirmando o recebimento
    return jsonify({
        "message": "Dados LTI recebidos com sucesso",
        "data": lti_data
    }), 200
    
# Endpoint para retornar a imagem 'foto.jpeg'
@app.route('/get-image', methods=['GET'])
def get_image():
    # Caminho absoluto para a imagem 'foto.jpeg' na raiz do projeto
    image_path = os.path.join(os.getcwd(), 'logo.png')

    # Verifica se a imagem existe e a retorna
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/jpeg')
    else:
        return jsonify({"error": "Imagem não encontrada"}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)

