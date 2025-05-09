from datetime import datetime
from bson import ObjectId
import re
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, email, password, name, role="user", created_at=None, _id=None):
        self._id = _id if _id else str(ObjectId())
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.name = name
        self.role = role
        self.created_at = created_at if created_at else datetime.utcnow()

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
            role=data.get('role', 'user'),
            created_at=data.get('created_at'),
            _id=data.get('_id')
        )

    def to_dict(self, include_password=False):
        user_dict = {
            '_id': self._id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'created_at': self.created_at
        }
        if include_password:
            user_dict['password_hash'] = self.password_hash
        return user_dict 