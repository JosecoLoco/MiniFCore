from pymongo import MongoClient
from bson import ObjectId
from init_filamentos import init_filamentos

# Conectar a MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['3Dfinal']

# Verificar si el administrador ya existe
admin = db.users.find_one({'email': 'admin@admin.com'})

if not admin:
    # Crear usuario administrador
    admin_data = {
        'nombre': 'Administrador',
        'email': 'admin@admin.com',
        'password': 'admin123',
        'is_admin': True
    }
    db.users.insert_one(admin_data)
    print("Usuario administrador creado exitosamente")
else:
    print("El usuario administrador ya existe")

# Crear algunas categorías de ejemplo si no existen
categorias = [
    {'nombre': 'Decoración'},
    {'nombre': 'Juguetes'},
    {'nombre': 'Accesorios'},
    {'nombre': 'Herramientas'}
]

for categoria in categorias:
    if not db.categorias.find_one({'nombre': categoria['nombre']}):
        db.categorias.insert_one(categoria)
        print(f"Categoría {categoria['nombre']} creada exitosamente")

print("Inicialización de la base de datos completada")

def init_database():
    print("Iniciando la configuración de la base de datos...")
    
    # Inicializar filamentos
    if init_filamentos():
        print("✓ Filamentos PLA inicializados correctamente")
    else:
        print("✗ Error al inicializar filamentos")

if __name__ == "__main__":
    init_database() 