from flask import Flask, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
from routes.print_jobs import print_jobs
from routes.auth import auth
from routes.categories import categories
from routes.products import products
from models.category import Category
from models.mongo import mongo
from datetime import datetime

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
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/3dprint_hub")
mongo.init_app(app)

# Inicializar categorías por defecto
def init_categories():
    """Inicializa las categorías por defecto si no existen"""
    if mongo.db.categories.count_documents({}) == 0:
        default_categories = [
            {
                'name': 'San Valentín',
                'description': 'Regalos románticos para el día de San Valentín',
                'icon': 'favorite',
                'created_at': datetime.utcnow()
            },
            {
                'name': 'Día de la Madre',
                'description': 'Regalos especiales para mamá',
                'icon': 'spa',
                'created_at': datetime.utcnow()
            },
            {
                'name': 'Halloween',
                'description': 'Disfraces y decoraciones para Halloween',
                'icon': 'mood_bad',
                'created_at': datetime.utcnow()
            },
            {
                'name': 'Navidad',
                'description': 'Decoraciones y regalos navideños',
                'icon': 'card_giftcard',
                'created_at': datetime.utcnow()
            },
            {
                'name': 'Pascua',
                'description': 'Decoraciones y regalos para Pascua',
                'icon': 'egg',
                'created_at': datetime.utcnow()
            }
        ]
        mongo.db.categories.insert_many(default_categories)
        print("Categorías inicializadas correctamente")

# Registrar blueprints
app.register_blueprint(print_jobs)
app.register_blueprint(auth, url_prefix='/api/auth')
app.register_blueprint(categories, url_prefix='/api/categories')
app.register_blueprint(products, url_prefix='/api/products')

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
            "/api/print-jobs/<id> (GET, PUT, DELETE)",
            "/api/categories (GET, POST)",
            "/api/products (GET, POST)"
        ]
    })

if __name__ == "__main__":
    with app.app_context():
        init_categories()  # Inicializar categorías al iniciar la aplicación
    app.run(debug=True, port=5000) 