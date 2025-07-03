# ElectroVision AI - Backend Boilerplate (Python Flask)

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import uuid
import subprocess
import fitz  # PyMuPDF for PDF
import ezdxf  # For DWG/DXF files

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return {"message": "ElectroVision AI Backend Running..."}

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    filename = secure_filename(file.filename)
    ext = filename.split('.')[-1].lower()
    uid = str(uuid.uuid4())
    filepath = os.path.join(UPLOAD_FOLDER, f"{uid}.{ext}")
    file.save(filepath)

    if ext == 'pdf':
        return handle_pdf(filepath)
    elif ext in ['dwg', 'dxf']:
        return handle_dwg_dxf(filepath)
    else:
        return jsonify({"error": "Unsupported file type"}), 400

def handle_pdf(filepath):
    doc = fitz.open(filepath)
    images = []
    for page_number in range(len(doc)):
        pix = doc[page_number].get_pixmap()
        img_path = f"{filepath}_page_{page_number}.png"
        pix.save(img_path)
        images.append(img_path)
    return jsonify({"status": "PDF processed", "images": images})

def handle_dwg_dxf(filepath):
    doc = ezdxf.readfile(filepath)
    components = []
    msp = doc.modelspace()
    for e in msp:
        if e.dxftype() in ['TEXT', 'MTEXT', 'LINE', 'CIRCLE', 'INSERT']:
            components.append({
                "type": e.dxftype(),
                "data": str(e.dxf)
            })
    return jsonify({"status": "DWG/DXF parsed", "components": components})

if __name__ == '__main__':
    app.run(debug=True, port=5000)