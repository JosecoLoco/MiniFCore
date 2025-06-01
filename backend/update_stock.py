from pymongo import MongoClient

def update_stock():
    try:
        # Conectar a MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['3Dfinal']
        
        # Actualizar el stock de todos los filamentos a 0
        resultado = db.filamentos.update_many(
            {},  # Actualizar todos los documentos
            {'$set': {'stock': 0}}
        )
        
        print(f"Se han actualizado {resultado.modified_count} filamentos")
        
    except Exception as e:
        print(f"Error al actualizar el stock: {e}")
    finally:
        client.close()
        print("Conexión a MongoDB cerrada")

if __name__ == '__main__':
    update_stock() 