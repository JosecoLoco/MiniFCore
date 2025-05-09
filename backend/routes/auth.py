from flask import Blueprint, request, jsonify
from models.user import User
from functools import wraps
import jwt
import os
from datetime import datetime, timedelta

auth = Blueprint('auth', __name__)

def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, os.getenv('JWT_SECRET', 'tu-clave-secreta'), algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token no proporcionado'}), 401
        try:
            token = token.split(' ')[1]  # Remover 'Bearer '
            data = jwt.decode(token, os.getenv('JWT_SECRET', 'tu-clave-secreta'), algorithms=['HS256'])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated

@auth.route('/api/auth/register', methods=['POST'])
def register():
    from app import mongo
    data = request.json

    # Validar campos requeridos
    required_fields = ['email', 'password', 'name', 'phone', 'city']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'El campo {field} es requerido'}), 400

    # Validar email
    if not User.validate_email(data['email']):
        return jsonify({'message': 'Email inválido'}), 400

    # Validar teléfono
    if not User.validate_phone(data['phone']):
        return jsonify({'message': 'Número de teléfono inválido'}), 400

    # Validar si el email ya existe
    if mongo.db.users.find_one({'email': data['email']}):
        return jsonify({'message': 'El email ya está registrado'}), 400

    # Validar contraseña
    is_valid_password, password_message = User.validate_password(data['password'])
    if not is_valid_password:
        return jsonify({'message': password_message}), 400

    # Crear usuario
    user = User(
        email=data['email'],
        password=data['password'],
        name=data['name'],
        phone=data['phone'],
        city=data['city']
    )

    # Guardar en la base de datos
    mongo.db.users.insert_one(user.to_dict(include_password=True))

    # Generar token
    token = create_token(user._id)

    return jsonify({
        'message': 'Usuario registrado exitosamente',
        'token': token,
        'user': {
            'id': user._id,
            'email': user.email,
            'name': user.name,
            'phone': user.phone,
            'country': user.country_info['name'],
            'country_code': user.country_info['code'],
            'city': user.city
        }
    }), 201

@auth.route('/api/auth/login', methods=['POST'])
def login():
    from app import mongo
    data = request.json

    # Validar campos requeridos
    if not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email y contraseña son requeridos'}), 400

    # Buscar usuario
    user_data = mongo.db.users.find_one({'email': data['email']})
    if not user_data:
        return jsonify({'message': 'Credenciales inválidas'}), 401

    user = User.from_dict(user_data)
    
    # Verificar contraseña
    if not user.check_password(data['password']):
        return jsonify({'message': 'Credenciales inválidas'}), 401

    # Generar token
    token = create_token(user._id)

    return jsonify({
        'message': 'Login exitoso',
        'token': token,
        'user': {
            'id': user._id,
            'email': user.email,
            'name': user.name
        }
    })

@auth.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user_id):
    from app import mongo
    user_data = mongo.db.users.find_one({'_id': current_user_id})
    if not user_data:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    user = User.from_dict(user_data)
    return jsonify(user.to_dict()) 