from models.mongo import mongo
from models.product import Product
from bson import ObjectId

def init_products():
    # Obtener las categorías existentes
    categories = list(mongo.db.categories.find())
    if not categories:
        print("No hay categorías disponibles. Primero ejecuta init_categories.py")
        return

    # Productos de ejemplo para cada categoría
    sample_products = {
        'San Valentín': [
            {
                'name': 'Corazón 3D con Mensaje',
                'description': 'Corazón personalizable con mensaje grabado, perfecto para San Valentín',
                'price': 25.99,
                'material': 'PLA',
                'print_time': '2 horas',
                'images': ['https://example.com/heart1.jpg']
            },
            {
                'name': 'Rosa Eterna',
                'description': 'Rosa impresa en 3D con acabado brillante',
                'price': 19.99,
                'material': 'PETG',
                'print_time': '3 horas',
                'images': ['https://example.com/rose1.jpg']
            },
            {
                'name': 'Marco de Fotos Corazón',
                'description': 'Marco de fotos con diseño de corazón para parejas',
                'price': 29.99,
                'material': 'PLA',
                'print_time': '4 horas',
                'images': ['https://example.com/frame1.jpg']
            }
        ],
        'Navidad': [
            {
                'name': 'Árbol de Navidad Decorativo',
                'description': 'Árbol de Navidad con luces LED integradas',
                'price': 39.99,
                'material': 'PLA',
                'print_time': '5 horas',
                'images': ['https://example.com/tree1.jpg']
            },
            {
                'name': 'Adorno de Santa Claus',
                'description': 'Santa Claus con detalles realistas',
                'price': 15.99,
                'material': 'PETG',
                'print_time': '2 horas',
                'images': ['https://example.com/santa1.jpg']
            },
            {
                'name': 'Copo de Nieve Giratorio',
                'description': 'Copo de nieve que gira con el viento',
                'price': 12.99,
                'material': 'PLA',
                'print_time': '1.5 horas',
                'images': ['https://example.com/snowflake1.jpg']
            }
        ],
        'Halloween': [
            {
                'name': 'Calabaza Iluminada',
                'description': 'Calabaza con luz LED integrada',
                'price': 22.99,
                'material': 'PLA',
                'print_time': '3 horas',
                'images': ['https://example.com/pumpkin1.jpg']
            },
            {
                'name': 'Máscara de Esqueleto',
                'description': 'Máscara de esqueleto con detalles realistas',
                'price': 29.99,
                'material': 'PETG',
                'print_time': '4 horas',
                'images': ['https://example.com/skull1.jpg']
            },
            {
                'name': 'Decoración de Araña',
                'description': 'Araña decorativa con movimiento',
                'price': 18.99,
                'material': 'PLA',
                'print_time': '2.5 horas',
                'images': ['https://example.com/spider1.jpg']
            }
        ]
    }

    # Limpiar productos existentes
    mongo.db.products.delete_many({})

    # Insertar productos de ejemplo
    for category in categories:
        category_name = category['name']
        if category_name in sample_products:
            for product_data in sample_products[category_name]:
                product = Product(
                    name=product_data['name'],
                    description=product_data['description'],
                    price=product_data['price'],
                    category_id=str(category['_id']),
                    material=product_data['material'],
                    print_time=product_data['print_time'],
                    images=product_data['images']
                )
                mongo.db.products.insert_one(product.to_dict())

    print("Productos de ejemplo inicializados correctamente")

if __name__ == '__main__':
    init_products() 