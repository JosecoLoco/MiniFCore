from datetime import datetime
from bson import ObjectId
import re
from werkzeug.security import generate_password_hash, check_password_hash
import phonenumbers
from phonenumbers import geocoder

class User:
    def __init__(self, email, password, name, phone, city=None, role="user", created_at=None, _id=None):
        self._id = _id if _id else str(ObjectId())
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.name = name
        self.phone = phone
        self.country_info = self._get_country_info(phone)
        self.city = city
        self.role = role
        self.created_at = created_at if created_at else datetime.utcnow()

    @staticmethod
    def _get_country_info(phone):
        try:
            # Parsear el número de teléfono
            parsed_number = phonenumbers.parse(phone)
            # Obtener el país
            country = geocoder.description_for_number(parsed_number, "es")
            # Obtener el código del país
            country_code = phonenumbers.region_code_for_number(parsed_number)
            return {
                'name': country,
                'code': country_code.lower()  # Convertir a minúsculas para las banderas
            }
        except:
            return {
                'name': None,
                'code': None
            }

    @staticmethod
    def validate_phone(phone):
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

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def from_dict(data):
        return User(
            email=data.get('email'),
            password=data.get('password') if 'password' in data else None,
            name=data.get('name'),
            phone=data.get('phone'),
            city=data.get('city'),
            role=data.get('role', 'user'),
            created_at=data.get('created_at'),
            _id=data.get('_id')
        )

    def to_dict(self, include_password=False):
        user_dict = {
            '_id': self._id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'country': self.country_info['name'],
            'country_code': self.country_info['code'],
            'city': self.city,
            'role': self.role,
            'created_at': self.created_at
        }
        if include_password:
            user_dict['password_hash'] = self.password_hash
        return user_dict 