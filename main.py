from flask import Flask, request, send_file, jsonify
from pikepdf import Pdf, PdfImage
import zipfile
import os
import io

app = Flask(__name__)

@app.route('/')
def home():
    return "Server running..."
    
@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado!"}), 400
    
    pdf_file = request.files['pdf']

    if pdf_file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado!"}), 400
    
    pdf_file.save('temp.pdf')

    pdf = Pdf.open('temp.pdf')
    pdf_images = []
    images = []
    pdf_images_not_duplicate = []

    for page in pdf.pages:
        for name, raw_image in page.images.items():
            pdf_images.append(PdfImage(raw_image))  

    for image in pdf_images:
        if image not in pdf_images_not_duplicate:
            pdf_images_not_duplicate.append(image)

    if not os.path.exists('images'):
            os.makedirs('images')
            
    indice = 1
    for image in pdf_images_not_duplicate:
        image_filename = f'images/image_{indice}'
        images.append(image.extract_to(fileprefix=image_filename))
        indice += 1

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
        for image_filename in images:
            zip_file.write(image_filename)
            os.remove(image_filename)

    zip_buffer.seek(0)
    os.remove('temp.pdf')

    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='images.zip')

if __name__ == '__main__':
    app.run(host='0.0.0.0')