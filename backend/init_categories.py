from app import mongo
from models.category import Category

def init_categories():
    # Lista de categorías por defecto
    default_categories = [
        {
            'name': 'San Valentín',
            'description': 'Productos especiales para el Día de San Valentín',
            'icon': 'favorite'
        },
        {
            'name': 'Día de la Madre',
            'description': 'Regalos especiales para el Día de la Madre',
            'icon': 'spa'
        },
        {
            'name': 'Halloween',
            'description': 'Diseños terroríficos para Halloween',
            'icon': 'mood_bad'
        },
        {
            'name': 'Navidad',
            'description': 'Decoraciones y regalos navideños',
            'icon': 'card_giftcard'
        },
        {
            'name': 'Pascuas',
            'description': 'Diseños especiales para la temporada de Pascua',
            'icon': 'egg'
        }
    ]

    # Limpiar categorías existentes
    mongo.db.categories.delete_many({})

    # Insertar nuevas categorías
    for cat_data in default_categories:
        category = Category(
            name=cat_data['name'],
            description=cat_data['description'],
            icon=cat_data['icon']
        )
        mongo.db.categories.insert_one(category.to_dict())

    print("Categorías inicializadas exitosamente")

if __name__ == '__main__':
    init_categories() 