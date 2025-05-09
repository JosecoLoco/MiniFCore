import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'stl', 'obj', 'gcode'}
UPLOAD_FOLDER = 'uploads'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        return filepath
    return None 