from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
import random

def init_filamentos():
    try:
        # Conectar a MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['3Dfinal']
        filamentos = db.filamentos

        # Eliminar filamentos existentes
        filamentos.delete_many({})

        # Colores PLA comunes
        colores_pla = [
            {
                'nombre': 'PLA Blanco',
                'descripcion': 'Filamento PLA blanco, ideal para todo tipo de impresiones',
                'color': 'Blanco',
                'material': 'PLA',
                'diametro': '1.75mm',
                'stock': random.randint(5, 15),
                'fecha_creacion': datetime.utcnow()
            },
            {
                'nombre': 'PLA Negro',
                'descripcion': 'Filamento PLA negro, acabado mate profesional',
                'color': 'Negro',
                'material': 'PLA',
                'diametro': '1.75mm',
                'stock': random.randint(5, 15),
                'fecha_creacion': datetime.utcnow()
            },
            {
                'nombre': 'PLA Rojo',
                'descripcion': 'Filamento PLA rojo brillante',
                'color': 'Rojo',
                'material': 'PLA',
                'diametro': '1.75mm',
                'stock': random.randint(5, 15),
                'fecha_creacion': datetime.utcnow()
            },
            {
                'nombre': 'PLA Azul',
                'descripcion': 'Filamento PLA azul cielo',
                'color': 'Azul',
                'material': 'PLA',
                'diametro': '1.75mm',
                'stock': random.randint(5, 15),
                'fecha_creacion': datetime.utcnow()
            },
            {
                'nombre': 'PLA Verde',
                'descripcion': 'Filamento PLA verde esmeralda',
                'color': 'Verde',
                'material': 'PLA',
                'diametro': '1.75mm',
                'stock': random.randint(5, 15),
                'fecha_creacion': datetime.utcnow()
            },
            {
                'nombre': 'PLA Amarillo',
                'descripcion': 'Filamento PLA amarillo brillante',
                'color': 'Amarillo',
                'material': 'PLA',
                'diametro': '1.75mm',
                'stock': random.randint(5, 15),
                'fecha_creacion': datetime.utcnow()
            },
            {
                'nombre': 'PLA Naranja',
                'descripcion': 'Filamento PLA naranja vibrante',
                'color': 'Naranja',
                'material': 'PLA',
                'diametro': '1.75mm',
                'stock': random.randint(5, 15),
                'fecha_creacion': datetime.utcnow()
            },
            {
                'nombre': 'PLA Morado',
                'descripcion': 'Filamento PLA morado elegante',
                'color': 'Morado',
                'material': 'PLA',
                'diametro': '1.75mm',
                'stock': random.randint(5, 15),
                'fecha_creacion': datetime.utcnow()
            },
            {
                'nombre': 'PLA Rosa',
                'descripcion': 'Filamento PLA rosa suave',
                'color': 'Rosa',
                'material': 'PLA',
                'diametro': '1.75mm',
                'stock': random.randint(5, 15),
                'fecha_creacion': datetime.utcnow()
            },
            {
                'nombre': 'PLA Dorado',
                'descripcion': 'Filamento PLA dorado metalizado',
                'color': 'Dorado',
                'material': 'PLA',
                'diametro': '1.75mm',
                'stock': random.randint(5, 15),
                'fecha_creacion': datetime.utcnow()
            }
        ]

        # Insertar los filamentos
        resultado = filamentos.insert_many(colores_pla)
        print(f"Se insertaron {len(resultado.inserted_ids)} filamentos PLA")

        # Ahora actualizar todos los productos para usar filamentos PLA aleatorios
        productos = db.productos.find()
        for producto in productos:
            # Seleccionar 1 o 2 filamentos PLA aleatorios para cada producto
            filamentos_seleccionados = random.sample(resultado.inserted_ids, random.randint(1, 2))
            
            # Actualizar el producto
            db.productos.update_one(
                {'_id': producto['_id']},
                {'$set': {'filamentos': filamentos_seleccionados}}
            )

        print("Productos actualizados con filamentos PLA")
        
        return True

    except Exception as e:
        print(f"Error en init_filamentos: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

# Para ejecutar la inicialización
if __name__ == "__main__":
    init_filamentos() 