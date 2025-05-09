from flask import Flask, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
from routes.print_jobs import print_jobs
from routes.auth import auth

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuración de MongoDB
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/impresiones3d")
mongo = PyMongo(app)

# Registrar blueprints
app.register_blueprint(print_jobs)
app.register_blueprint(auth)

@app.route("/")
def home():
    return jsonify({
        "mensaje": "API de Impresiones 3D",
        "estado": "activo",
        "rutas_disponibles": [
            "/api/auth/register (POST)",
            "/api/auth/login (POST)",
            "/api/auth/me (GET)",
            "/api/print-jobs (GET, POST)",
            "/api/print-jobs/<id> (GET, PUT, DELETE)"
        ]
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000) 