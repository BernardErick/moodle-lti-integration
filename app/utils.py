# app/utils.py
import qrcode
import urllib.parse
import json
import io
from PIL import Image
import base64

def generate_qr_data(lti_data):
    post_url = "http://localhost:5000/receive-lti-data"
    lti_data_json = json.dumps(lti_data)
    encoded_data = urllib.parse.quote(lti_data_json)
    return f"{post_url}?data={encoded_data}"


def create_qr_image(data):
    """
    Cria um QR Code a partir dos dados fornecidos e retorna a imagem como base64.
    """
    # Cria o objeto QR Code
    qr = qrcode.QRCode(
        version=10,  # Ajuste a versão conforme necessário (1 a 40)
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(data)
    qr.make(fit=True)  # Aqui, você pode definir o fit para False ou True, dependendo do comportamento desejado.
    
    # Cria a imagem do QR Code
    img = qr.make_image(fill="black", back_color="white")
    
    # Converte a imagem do QR Code para RGB (para garantir que tenha o mesmo modo que a imagem de fundo)
    qr_img_rgb = img.convert('RGB')

    # Agora vamos criar uma nova imagem com o fundo colorido e o QR Code no meio
    width, height = qr_img_rgb.size
    background_color = '#3c7593'  # Cor de fundo ao redor do QR Code

    # Criar uma nova imagem maior, com o fundo colorido
    new_img = Image.new('RGB', (width + 40, height + 40), background_color)  # Adicionando uma borda de 20px em cada lado

    # Colar a imagem do QR Code no centro da nova imagem
    new_img.paste(qr_img_rgb, (20, 20))

    # Salva a imagem com o fundo colorido em um buffer (BytesIO)
    buffered = io.BytesIO()
    new_img.save(buffered, format='PNG')
    buffered.seek(0)

    # Retorna a imagem como uma string base64
    return base64.b64encode(buffered.getvalue()).decode("utf-8")
