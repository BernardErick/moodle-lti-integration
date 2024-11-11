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

def create_qr_image(qr_data):
    qr = qrcode.QRCode(
        version=10,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill='black', back_color='white')
    qr_img_rgb = qr_img.convert('RGB')

    width, height = qr_img_rgb.size
    new_img = Image.new('RGB', (width + 40, height + 40), '#3c7593')
    new_img.paste(qr_img_rgb, (20, 20))

    img = io.BytesIO()
    new_img.save(img, format='PNG')
    img.seek(0)
    
    return base64.b64encode(img.getvalue()).decode('utf-8')
