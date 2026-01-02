import os
import uuid
from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from utils.image_converter import convert_images_to_pdf, compress_image
from utils.pdf_editor import merge_pdfs, split_pdf, rotate_pages, delete_pages

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
COUNTER_FILE = os.path.join(os.path.dirname(__file__), 'usage_counter.txt')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp', 'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def increment_counter():
    count = 0
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'r') as f:
            try:
                count = int(f.read().strip())
            except:
                count = 0
    count += 1
    with open(COUNTER_FILE, 'w') as f:
        f.write(str(count))
    return count

def get_counter():
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'r') as f:
            try:
                return int(f.read().strip())
            except:
                return 0
    return 0

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    files = request.files.getlist('files')
    uploaded_files = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            file.save(file_path)
            uploaded_files.append({
                "original_name": filename,
                "server_name": unique_name,
                "path": file_path
            })
            
    return jsonify({"files": uploaded_files}), 200

@app.route('/api/convert', methods=['POST'])
def convert():
    increment_counter()
    data = request.json
    server_names = data.get('files', [])
    output_filename = data.get('output_name', 'converted.pdf')
    
    if not server_names:
        return jsonify({"error": "No files provided"}), 400
        
    image_paths = [os.path.join(app.config['UPLOAD_FOLDER'], name) for name in server_names]
    pdf_filename = f"out_{uuid.uuid4()}.pdf"
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
    
    success, result = convert_images_to_pdf(image_paths, pdf_path)
    
    if success:
        return jsonify({"pdf_url": f"/api/download/{pdf_filename}", "filename": pdf_filename}), 200
    else:
        return jsonify({"error": result}), 500

@app.route('/api/merge', methods=['POST'])
def merge():
    data = request.json
    server_names = data.get('files', [])
    
    if len(server_names) < 2:
        return jsonify({"error": "At least 2 files required for merging"}), 400
        
    pdf_paths = [os.path.join(app.config['UPLOAD_FOLDER'], name) for name in server_names]
    output_filename = f"merged_{uuid.uuid4()}.pdf"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    success, result = merge_pdfs(pdf_paths, output_path)
    
    if success:
        return jsonify({"pdf_url": f"/api/download/{output_filename}", "filename": output_filename}), 200
    else:
        return jsonify({"error": result}), 500

@app.route('/api/rotate', methods=['POST'])
def rotate():
    data = request.json
    server_name = data.get('file')
    rotation_map = data.get('rotations', {}) # {page_index: angle}
    
    if not server_name:
        return jsonify({"error": "No file provided"}), 400
        
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], server_name)
    output_filename = f"rotated_{uuid.uuid4()}.pdf"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    success, result = rotate_pages(input_path, output_path, rotation_map)
    
    if success:
        return jsonify({"pdf_url": f"/api/download/{output_filename}", "filename": output_filename}), 200
    else:
        return jsonify({"error": result}), 500

@app.route('/api/delete-pages', methods=['POST'])
def delete():
    increment_counter()
    data = request.json
    server_name = data.get('file')
    pages = data.get('pages', []) # [1, 3, 5]
    
    if not server_name:
        return jsonify({"error": "No file provided"}), 400
        
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], server_name)
    output_filename = f"edited_{uuid.uuid4()}.pdf"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    success, result = delete_pages(input_path, output_path, pages)
    
    if success:
        return jsonify({"pdf_url": f"/api/download/{output_filename}", "filename": output_filename}), 200
    else:
        return jsonify({"error": result}), 500

@app.route('/api/compress', methods=['POST'])
def compress():
    increment_counter()
    data = request.json
    server_name = data.get('file')
    quality = data.get('quality', 60)
    
    if not server_name:
        return jsonify({"error": "No file provided"}), 400
        
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], server_name)
    output_filename = f"compressed_{uuid.uuid4()}.jpg"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    success, result = compress_image(input_path, output_path, quality=quality)
    
    if success:
        return jsonify({"url": f"/api/download/{output_filename}", "filename": output_filename}), 200
    else:
        return jsonify({"error": result}), 500

@app.route('/api/counter', methods=['GET'])
def counter():
    return jsonify({"count": get_counter()}), 200

@app.route('/api/download/<filename>', methods=['GET'])
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
