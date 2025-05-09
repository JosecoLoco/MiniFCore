from datetime import datetime
from bson import ObjectId
import re
from werkzeug.security import generate_password_hash, check_password_hash
import phonenumbers
from phonenumbers import geocoder
import bcrypt

class User:
    def __init__(self, name, email, password, phone, city=None):
        self.name = name
        self.email = email
        self.password = self._encrypt_password(password)
        self.phone = phone
        self.country = self._get_country_from_phone(phone)
        self.city = city
        self.created_at = datetime.utcnow()
        self.is_admin = False
        self.last_activity = datetime.utcnow()

    @staticmethod
    def _encrypt_password(password):
        """Encripta la contraseña usando bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    def verify_password(self, password):
        """Verifica si la contraseña coincide con la encriptada"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

    def _get_country_from_phone(self, phone):
        """Obtiene el país basado en el código del teléfono"""
        try:
            parsed_number = phonenumbers.parse(phone)
            country_code = phonenumbers.region_code_for_number(parsed_number)
            return country_code
        except:
            return None

    @staticmethod
    def validate_phone(phone):
        """Valida si el número de teléfono es válido"""
        try:
            parsed_number = phonenumbers.parse(phone)
            return phonenumbers.is_valid_number(parsed_number)
        except:
            return False

    @staticmethod
    def validate_email(email):
        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(email_regex.match(email))

    @staticmethod
    def validate_password(password):
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        if not re.search(r"[A-Z]", password):
            return False, "La contraseña debe contener al menos una mayúscula"
        if not re.search(r"[a-z]", password):
            return False, "La contraseña debe contener al menos una minúscula"
        if not re.search(r"\d", password):
            return False, "La contraseña debe contener al menos un número"
        return True, "Contraseña válida"

    def to_dict(self, include_password=False):
        """Convierte el objeto a un diccionario para almacenar en MongoDB"""
        user_dict = {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'country': self.country,
            'city': self.city,
            'created_at': self.created_at,
            'is_admin': self.is_admin,
            'last_activity': self.last_activity
        }
        
        if include_password:
            user_dict['password'] = self.password.decode('utf-8') if isinstance(self.password, bytes) else self.password
            
        return user_dict

    @classmethod
    def from_dict(cls, data):
        """Crea un objeto User desde un diccionario de MongoDB"""
        user = cls(
            name=data['name'],
            email=data['email'],
            password='',  # No necesitamos la contraseña para crear el objeto
            phone=data['phone'],
            city=data.get('city')
        )
        # Convertir la contraseña a bytes si es string
        password = data['password']
        if isinstance(password, str):
            password = password.encode('utf-8')
        user.password = password
        user.created_at = data['created_at']
        user.is_admin = data.get('is_admin', False)
        user.last_activity = data.get('last_activity', datetime.utcnow())
        return user

    def update_last_activity(self):
        """Actualiza el timestamp de última actividad"""
        self.last_activity = datetime.utcnow()
        return self.last_activity 