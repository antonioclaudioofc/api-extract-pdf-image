from flask import Flask, request, send_file
from pikepdf import Pdf, PdfImage
import zipfile
import os
import io

app = Flask(__name__)

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return 'Nenhum arquivo enviado!', 400
    
    pdf_file = request.files['pdf']

    if pdf_file.filename == '':
        return 'Nenhum arquivo selecionado!', 400
    
    pdf_file.save('temp.pdf')

    pdf = Pdf.open('temp.pdf')
    pdf_image = []
    images = []
    pdf_images_not_duplicate = []

    for page in enumerate(pdf.pages):
        for raw_image in page.images.items():
            pdf_image.append(PdfImage(raw_image))

    for image in pdf_image:
        if image not in pdf_images_not_duplicate:
            pdf_images_not_duplicate.append(image)

    indice = 1
    for image in pdf_images_not_duplicate:
        image_filename = f'image_{indice}'
        image.extract_to(fileprefix=image_filename)
        images.append(image_filename)
        indice += 1

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
        for image_filename in images:
            zip_file.write(image_filename)
            os.remove(image_filename)

    zip_buffer.seek(0)
    os.remove('temp.pdf')

    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, attachment_filename='images.zip')

if __name__ == '__main__':
    app.run(debug=True)