from datetime import datetime
from bson import ObjectId

class Category:
    def __init__(self, name, description, icon):
        self.name = name
        self.description = description
        self.icon = icon
        self.created_at = datetime.utcnow()

    def to_dict(self):
        """Convierte el objeto a un diccionario para almacenar en MongoDB"""
        return {
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        """Crea un objeto Category desde un diccionario de MongoDB"""
        category = cls(
            name=data['name'],
            description=data['description'],
            icon=data['icon']
        )
        category.created_at = data.get('created_at', datetime.utcnow())
        return category 