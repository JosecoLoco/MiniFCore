from datetime import datetime
from bson import ObjectId

class Product:
    def __init__(self, name, description, price, category_id, material, print_time, images=None):
        self.name = name
        self.description = description
        self.price = price
        self.category_id = category_id
        self.material = material
        self.print_time = print_time
        self.images = images or []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        """Convierte el objeto a un diccionario para almacenar en MongoDB"""
        return {
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category_id': self.category_id,
            'material': self.material,
            'print_time': self.print_time,
            'images': self.images,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        """Crea un objeto Product desde un diccionario de MongoDB"""
        product = cls(
            name=data['name'],
            description=data['description'],
            price=data['price'],
            category_id=data['category_id'],
            material=data['material'],
            print_time=data['print_time'],
            images=data.get('images', [])
        )
        product.created_at = data['created_at']
        product.updated_at = data.get('updated_at', data['created_at'])
        return product

    def update(self, data):
        """Actualiza los campos del producto"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        return self.to_dict() 