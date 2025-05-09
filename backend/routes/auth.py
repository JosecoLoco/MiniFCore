from flask import Blueprint, request, jsonify
from models.user import User
from models.mongo import mongo
from datetime import datetime, timedelta
import jwt
import os
from functools import wraps

auth = Blueprint('auth', __name__)

# Configuración del token JWT
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')
JWT_ALGORITHM = 'HS256'
INACTIVITY_TIMEOUT = 15  # segundos

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token no proporcionado'}), 401
        
        try:
            token = token.split(' ')[1]  # Eliminar 'Bearer ' del token
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            current_user = mongo.db.users.find_one({'_id': data['user_id']})
            
            if not current_user:
                return jsonify({'message': 'Usuario no encontrado'}), 401

            # Verificar timeout de inactividad
            last_activity = current_user.get('last_activity', datetime.utcnow())
            if datetime.utcnow() - last_activity > timedelta(seconds=INACTIVITY_TIMEOUT):
                return jsonify({'message': 'Sesión expirada por inactividad'}), 401

            # Actualizar timestamp de última actividad
            mongo.db.users.update_one(
                {'_id': current_user['_id']},
                {'$set': {'last_activity': datetime.utcnow()}}
            )

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = ['name', 'email', 'password', 'phone']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Faltan campos requeridos'}), 400
    
    # Validar email único
    if mongo.db.users.find_one({'email': data['email']}):
        return jsonify({'message': 'El email ya está registrado'}), 400
    
    # Validar teléfono
    if not User.validate_phone(data['phone']):
        return jsonify({'message': 'Número de teléfono inválido'}), 400
    
    # Crear usuario
    user = User(
        name=data['name'],
        email=data['email'],
        password=data['password'],
        phone=data['phone'],
        city=data.get('city')
    )
    
    # Guardar en la base de datos
    user_dict = user.to_dict(include_password=True)
    result = mongo.db.users.insert_one(user_dict)
    user_dict['_id'] = str(result.inserted_id)
    
    # Eliminar la contraseña antes de enviar la respuesta
    user_dict.pop('password', None)
    
    return jsonify({
        'message': 'Usuario registrado exitosamente',
        'user': user_dict
    }), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Credenciales incompletas'}), 400
    
    user_data = mongo.db.users.find_one({'email': data['email']})
    if not user_data:
        return jsonify({'message': 'Usuario no encontrado'}), 401
    
    user = User.from_dict(user_data)
    if not user.verify_password(data['password']):
        return jsonify({'message': 'Contraseña incorrecta'}), 401
    
    # Actualizar timestamp de última actividad
    user.update_last_activity()
    mongo.db.users.update_one(
        {'_id': user_data['_id']},
        {'$set': {'last_activity': user.last_activity}}
    )
    
    # Generar token
    token = jwt.encode({
        'user_id': str(user_data['_id']),
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    user_dict = user.to_dict()
    user_dict['_id'] = str(user_data['_id'])
    
    return jsonify({
        'message': 'Login exitoso',
        'token': token,
        'user': user_dict
    }), 200

@auth.route('/check-session', methods=['GET'])
@token_required
def check_session(current_user):
    return jsonify({
        'message': 'Sesión válida',
        'user': current_user
    }), 200 