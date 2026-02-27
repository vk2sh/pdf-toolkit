import os
from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfMerger
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)

import os

# Detect if running on Render
if os.environ.get("RENDER"):
    BASE_FOLDER = "/tmp"
else:
    BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_FOLDER, "uploads")
MERGED_FOLDER = os.path.join(BASE_FOLDER, "merged")
CONVERTED_FOLDER = os.path.join(BASE_FOLDER, "converted")
COMPRESSED_FOLDER = os.path.join(BASE_FOLDER, "compressed")

for folder in [UPLOAD_FOLDER, MERGED_FOLDER, CONVERTED_FOLDER, COMPRESSED_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# ---------------- ROUTES ---------------- #

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/merge-page')
def merge_page():
    return render_template('merge.html')

@app.route('/compress-page')
def compress_page():
    return render_template('compress.html')

@app.route('/jpg-to-pdf-page')
def jpg_to_pdf_page():
    return render_template('jpg_to_pdf.html')

# ---------------- PDF MERGE ---------------- #

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    files = request.files.getlist("pdfs")
    merger = PdfMerger()

    for file in files:
        filepath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(filepath)
        merger.append(filepath)

    output_path = os.path.join(MERGED_FOLDER, "merged_output.pdf")
    merger.write(output_path)
    merger.close()

    return send_file(output_path, as_attachment=True)

# ---------------- IMAGE COMPRESSION ---------------- #

@app.route('/compress', methods=['POST'])
def compress_image():
    file = request.files['image']
    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(filepath)

    img = Image.open(filepath)
    output_path = os.path.join(COMPRESSED_FOLDER, "compressed_" + file.filename)

    img.save(output_path, optimize=True, quality=40)  # 40 = compression level

    return send_file(output_path, as_attachment=True)

# ---------------- JPG TO PDF ---------------- #

@app.route('/jpg-to-pdf', methods=['POST'])
def jpg_to_pdf():
    file = request.files['image']
    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(filepath)

    img = Image.open(filepath)
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    output_path = os.path.join(CONVERTED_FOLDER, file.filename.split('.')[0] + ".pdf")
    img.save(output_path, "PDF", resolution=100.0)

    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)