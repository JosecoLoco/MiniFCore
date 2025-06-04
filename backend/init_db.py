from pymongo import MongoClient
from datetime import datetime

def init_db():
    try:
        # Conectar a MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['3Dfinal']
        
        # Limpiar colecciones existentes
        db.categorias.delete_many({})
        db.productos.delete_many({})
        db.filamentos.delete_many({})
        
        # Insertar categorías
        categorias = [
            {
                "nombre": "Decoración",
                "descripcion": "Piezas decorativas para el hogar y oficina"
            },
            {
                "nombre": "Juguetes",
                "descripcion": "Juguetes y figuras coleccionables"
            },
            {
                "nombre": "Herramientas",
                "descripcion": "Herramientas y accesorios impresos en 3D"
            },
            {
                "nombre": "Arte",
                "descripcion": "Piezas artísticas y esculturas"
            },
            {
                "nombre": "Electrónica",
                "descripcion": "Carcasas y componentes para electrónica"
            }
        ]
        db.categorias.insert_many(categorias)
        
        # Insertar filamentos
        filamentos = [
            {
                "nombre": "PLA Blanco",
                "color": "Blanco",
                "material": "PLA",
                "diametro": "1.75mm",
                "stock": 15
            },
            {
                "nombre": "PLA Negro",
                "color": "Negro",
                "material": "PLA",
                "diametro": "1.75mm",
                "stock": 15
            },
            {
                "nombre": "PLA Verde",
                "color": "Verde",
                "material": "PLA",
                "diametro": "1.75mm",
                "stock": 15
            },
            {
                "nombre": "PLA Rojo",
                "color": "Rojo",
                "material": "PLA",
                "diametro": "1.75mm",
                "stock": 15
            },
            {
                "nombre": "PLA Azul",
                "color": "Azul",
                "material": "PLA",
                "diametro": "1.75mm",
                "stock": 15
            },
            {
                "nombre": "PLA Transparente",
                "color": "Transparente",
                "material": "PLA",
                "diametro": "1.75mm",
                "stock": 15
            }
        ]
        filamentos_ids = db.filamentos.insert_many(filamentos).inserted_ids
        
        # Insertar productos
        productos = [
            {
                "nombre": "Maceta Decorativa",
                "descripcion": "Maceta moderna con diseño geométrico",
                "precio": 25.99,
                "categoria": "Decoración",
                "stock": 10,
                "tiempo_entrega": "3-5 días",
                "tamaño_maximo": "15x15x20 cm",
                "filamentos": [filamentos_ids[0], filamentos_ids[1], filamentos_ids[2]],
                "incluye": ["Maceta", "Plato base", "Instrucciones de cuidado"]
            },
            {
                "nombre": "Lámpara LED",
                "descripcion": "Lámpara de mesa con diseño único",
                "precio": 35.99,
                "categoria": "Decoración",
                "stock": 8,
                "tiempo_entrega": "4-6 días",
                "tamaño_maximo": "20x20x30 cm",
                "filamentos": [filamentos_ids[0], filamentos_ids[5]],
                "incluye": ["Base de lámpara", "Cable USB", "Bombilla LED"]
            },
            {
                "nombre": "Robot Articulado",
                "descripcion": "Robot articulado con movimiento completo",
                "precio": 29.99,
                "categoria": "Juguetes",
                "stock": 15,
                "tiempo_entrega": "2-4 días",
                "tamaño_maximo": "10x10x15 cm",
                "filamentos": [filamentos_ids[3], filamentos_ids[4], filamentos_ids[1]],
                "incluye": ["Robot", "Manual de ensamblaje", "Herramientas"]
            },
            {
                "nombre": "Dinosaurio Coleccionable",
                "descripcion": "Dinosaurio detallado para coleccionistas",
                "precio": 19.99,
                "categoria": "Juguetes",
                "stock": 12,
                "tiempo_entrega": "3-5 días",
                "tamaño_maximo": "15x8x10 cm",
                "filamentos": [filamentos_ids[2], filamentos_ids[1]],
                "incluye": ["Dinosaurio", "Base de exhibición"]
            },
            {
                "nombre": "Organizador de Herramientas",
                "descripcion": "Organizador modular para herramientas",
                "precio": 22.99,
                "categoria": "Herramientas",
                "stock": 10,
                "tiempo_entrega": "3-5 días",
                "tamaño_maximo": "25x15x10 cm",
                "filamentos": [filamentos_ids[1], filamentos_ids[0]],
                "incluye": ["Base", "Separadores", "Instrucciones"]
            },
            {
                "nombre": "Soporte para Teléfono",
                "descripcion": "Soporte ajustable para teléfono",
                "precio": 12.99,
                "categoria": "Herramientas",
                "stock": 20,
                "tiempo_entrega": "2-3 días",
                "tamaño_maximo": "10x5x15 cm",
                "filamentos": [filamentos_ids[0], filamentos_ids[1]],
                "incluye": ["Soporte", "Base ajustable"]
            }
        ]
        db.productos.insert_many(productos)
        
        print("Base de datos inicializada correctamente")
        
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    init_db() 