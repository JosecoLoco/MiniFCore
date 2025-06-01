from pymongo import MongoClient
from datetime import datetime

def init_filamentos():
    try:
        # Conectar a MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['3Dfinal']
        
        # Verificar si la colección ya existe
        if 'filamentos' in db.list_collection_names():
            print("La colección 'filamentos' ya existe")
            return

        # Crear la colección de filamentos
        filamentos = db['filamentos']

        # Datos de ejemplo para filamentos
        filamentos_ejemplo = [
            {
                'nombre': 'PLA Negro',
                'descripcion': 'Filamento PLA de color negro, ideal para impresiones generales',
                'color': 'Negro',
                'material': 'PLA',
                'diametro': '1.75mm',
                'stock': 1000,
                'fecha_creacion': datetime.utcnow()
            },
            {
                'nombre': 'PLA Blanco',
                'descripcion': 'Filamento PLA de color blanco, ideal para impresiones generales',
                'color': 'Blanco',
                'material': 'PLA',
                'diametro': '1.75mm',
                'stock': 1500,
                'fecha_creacion': datetime.utcnow()
            },
            {
                'nombre': 'ABS Rojo',
                'descripcion': 'Filamento ABS de color rojo, ideal para piezas resistentes',
                'color': 'Rojo',
                'material': 'ABS',
                'diametro': '1.75mm',
                'stock': 800,
                'fecha_creacion': datetime.utcnow()
            },
            {
                'nombre': 'PETG Transparente',
                'descripcion': 'Filamento PETG transparente, ideal para piezas resistentes y flexibles',
                'color': 'Transparente',
                'material': 'PETG',
                'diametro': '1.75mm',
                'stock': 1200,
                'fecha_creacion': datetime.utcnow()
            },
            {
                'nombre': 'TPU Negro',
                'descripcion': 'Filamento TPU de color negro, ideal para piezas flexibles',
                'color': 'Negro',
                'material': 'TPU',
                'diametro': '1.75mm',
                'stock': 500,
                'fecha_creacion': datetime.utcnow()
            },
            {
                'nombre': 'PLA Verde',
                'descripcion': 'Filamento PLA de color verde, ideal para impresiones generales',
                'color': 'Verde',
                'material': 'PLA',
                'diametro': '1.75mm',
                'stock': 750,
                'fecha_creacion': datetime.utcnow()
            },
            {
                'nombre': 'ABS Azul',
                'descripcion': 'Filamento ABS de color azul, ideal para piezas resistentes',
                'color': 'Azul',
                'material': 'ABS',
                'diametro': '1.75mm',
                'stock': 600,
                'fecha_creacion': datetime.utcnow()
            },
            {
                'nombre': 'PETG Negro',
                'descripcion': 'Filamento PETG de color negro, ideal para piezas resistentes',
                'color': 'Negro',
                'material': 'PETG',
                'diametro': '1.75mm',
                'stock': 900,
                'fecha_creacion': datetime.utcnow()
            }
        ]

        # Insertar los filamentos de ejemplo
        resultado = filamentos.insert_many(filamentos_ejemplo)
        print(f"Se han insertado {len(resultado.inserted_ids)} filamentos de ejemplo")

        # Crear índices para optimizar las búsquedas
        filamentos.create_index('nombre', unique=True)
        filamentos.create_index('material')
        filamentos.create_index('color')
        print("Índices creados correctamente")

    except Exception as e:
        print(f"Error al inicializar la colección de filamentos: {e}")
    finally:
        client.close()
        print("Conexión a MongoDB cerrada")

if __name__ == '__main__':
    init_filamentos() 