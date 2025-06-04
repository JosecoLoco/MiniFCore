from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from pedido_flow import PedidoFlow
from sugerencias_flow import SugerenciasFlow

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
# Configurar CORS para permitir todas las rutas y métodos
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

app.config['SECRET_KEY'] = 'tu_clave_secreta'  # En producción, usar una clave segura

# Configuración de MongoDB
try:
    client = MongoClient('mongodb://localhost:27017/')
    # Verificar la conexión
    client.server_info()
    db = client['3Dfinal']
    print("Conexión exitosa a MongoDB - Base de datos: 3Dfinal")
except Exception as e:
    print(f"Error al conectar con MongoDB: {e}")


def generate_token(user_id, rol):
    payload = {
        'user_id': str(user_id),
        'rol': rol,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

# Decorador para verificar token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Permitir solicitudes OPTIONS sin token
        if request.method == 'OPTIONS':
            return '', 200

        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token no proporcionado'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = db.users.find_one({'_id': ObjectId(data['user_id'])})
            if not current_user:
                return jsonify({'message': 'Usuario no encontrado'}), 401
        except:
            return jsonify({'message': 'Token inválido'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# Ruta de login
@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    
    if not auth or not auth.get('email') or not auth.get('password'):
        return jsonify({'message': 'Credenciales incompletas'}), 400
    
    user = db.users.find_one({'email': auth.get('email')})
    
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 401
    
    # Verificar si es el administrador
    if auth.get('email') == 'admin@admin.com' and auth.get('password') == 'admin123':
        token = generate_token(user['_id'], 'administrador')
        return jsonify({
            'token': token,
            'rol': 'administrador'
        })
    
    # Para otros usuarios, verificar la contraseña normal
    if auth.get('password') != user.get('password'):
        return jsonify({'message': 'Contraseña incorrecta'}), 401
    
    # Determinar el rol basado en is_admin
    rol = 'administrador' if user.get('is_admin', False) else 'usuario'
    
    token = generate_token(user['_id'], rol)
    
    return jsonify({
        'token': token,
        'rol': rol
    })

# Rutas para Usuarios
@app.route('/users', methods=['GET', 'OPTIONS'])
@token_required
def get_usuarios(current_user):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        usuarios = list(db.users.find())
        for usuario in usuarios:
            usuario['_id'] = str(usuario['_id'])
            # No enviar la contraseña en la respuesta
            if 'password' in usuario:
                del usuario['password']
        return jsonify(usuarios)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users', methods=['POST', 'OPTIONS'])
def crear_usuario():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        usuario = request.json
        resultado = db.users.insert_one(usuario)
        return jsonify({"mensaje": "Usuario creado", "id": str(resultado.inserted_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users/<user_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def eliminar_usuario(current_user, user_id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        resultado = db.users.delete_one({'_id': ObjectId(user_id)})
        if resultado.deleted_count == 0:
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify({"mensaje": "Usuario eliminado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rutas para Productos
@app.route('/productos', methods=['GET'])
@token_required
def get_productos(current_user):
    try:
        productos = list(db.productos.find())
        for producto in productos:
            producto['_id'] = str(producto['_id'])
            if 'filamentos' in producto:
                filamentos = list(db.filamentos.find({'_id': {'$in': producto['filamentos']}}))
                producto['filamentos'] = [{
                    '_id': str(f['_id']),
                    'nombre': f['nombre'],
                    'color': f['color'],
                    'material': f['material'],
                    'diametro': f['diametro']
                } for f in filamentos]
        return jsonify(productos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/productos', methods=['POST'])
@token_required
def crear_producto(current_user):
    if not current_user.get('is_admin', False):
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        data = request.get_json()
        filamentos_ids = []
        if 'filamentos' in data:
            filamentos_nombres = [f.strip() for f in data['filamentos'].split(',')]
            for nombre in filamentos_nombres:
                filamento = db.filamentos.find_one({'nombre': nombre})
                if filamento:
                    filamentos_ids.append(filamento['_id'])
        
        producto = {
            'nombre': data['nombre'],
            'descripcion': data['descripcion'],
            'precio': float(data['precio']),
            'categoria': data['categoria'],
            'stock': int(data['stock']),
            'tiempo_entrega': data['tiempo_entrega'],
            'filamentos': filamentos_ids,
            'tamaño_maximo': data.get('tamaño_maximo', '')
        }
        
        result = db.productos.insert_one(producto)
        producto['_id'] = str(result.inserted_id)
        return jsonify(producto), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/productos/<producto_id>', methods=['PUT'])
@token_required
def actualizar_producto(current_user, producto_id):
    if not current_user.get('is_admin', False):
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        data = request.get_json()
        filamentos_ids = []
        if 'filamentos' in data:
            filamentos_nombres = [f.strip() for f in data['filamentos'].split(',')]
            for nombre in filamentos_nombres:
                filamento = db.filamentos.find_one({'nombre': nombre})
                if filamento:
                    filamentos_ids.append(filamento['_id'])
        
        producto = {
            'nombre': data['nombre'],
            'descripcion': data['descripcion'],
            'precio': float(data['precio']),
            'categoria': data['categoria'],
            'stock': int(data['stock']),
            'tiempo_entrega': data['tiempo_entrega'],
            'filamentos': filamentos_ids,
            'tamaño_maximo': data.get('tamaño_maximo', '')
        }
        
        result = db.productos.update_one(
            {'_id': ObjectId(producto_id)},
            {'$set': producto}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        producto['_id'] = producto_id
        return jsonify(producto)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/productos/<producto_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def eliminar_producto(current_user, producto_id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        resultado = db.productos.delete_one({'_id': ObjectId(producto_id)})
        if resultado.deleted_count == 0:
            return jsonify({"error": "Producto no encontrado"}), 404
        return jsonify({"mensaje": "Producto eliminado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rutas para Pedidos
@app.route('/pedidos', methods=['GET'])
@token_required
def obtener_pedidos(current_user):
    try:
        print("Iniciando obtención de pedidos...")
        
        # Obtener todos los pedidos
        pedidos = list(db.pedidos.find())
        print(f"Pedidos encontrados: {len(pedidos)}")
        
        # Convertir ObjectId a string y agregar información del producto
        pedidos_procesados = []
        for pedido in pedidos:
            try:
                print(f"Procesando pedido: {pedido.get('_id')}")
                
                # Convertir ObjectId a string
                pedido['_id'] = str(pedido['_id'])
                
                # Obtener información del producto
                if 'producto_id' in pedido:
                    producto = db.productos.find_one({'_id': ObjectId(pedido['producto_id'])})
                    if producto:
                        pedido['producto'] = {
                            '_id': str(producto['_id']),
                            'nombre': producto.get('nombre', 'Producto no disponible'),
                            'precio': producto.get('precio', 0)
                        }
                    else:
                        print(f"Producto no encontrado para pedido {pedido['_id']}")
                
                # Obtener información del cliente
                if 'cliente_id' in pedido:
                    cliente = db.usuarios.find_one({'_id': ObjectId(pedido['cliente_id'])})
                    if cliente:
                        pedido['cliente'] = {
                            '_id': str(cliente['_id']),
                            'nombre': cliente.get('nombre', 'Cliente no disponible'),
                            'email': cliente.get('email', '')
                        }
                    else:
                        print(f"Cliente no encontrado para pedido {pedido['_id']}")
                
                # Convertir fechas
                if 'fecha' in pedido:
                    if isinstance(pedido['fecha'], datetime):
                        pedido['fecha'] = pedido['fecha'].strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        print(f"Fecha inválida en pedido {pedido['_id']}")
                
                if 'fecha_entrega' in pedido:
                    if isinstance(pedido['fecha_entrega'], datetime):
                        pedido['fecha_entrega'] = pedido['fecha_entrega'].strftime('%Y-%m-%d')
                    else:
                        print(f"Fecha de entrega inválida en pedido {pedido['_id']}")
                
                pedidos_procesados.append(pedido)
                print(f"Pedido {pedido['_id']} procesado correctamente")
                
            except Exception as e:
                print(f"Error procesando pedido {pedido.get('_id')}: {e}")
                continue
        
        print(f"Total de pedidos procesados: {len(pedidos_procesados)}")
        return jsonify(pedidos_procesados)
        
    except Exception as e:
        print(f"Error general al obtener pedidos: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/pedidos', methods=['POST'])
@token_required
def crear_pedido(current_user):
    try:
        pedido = request.json
        
        # Validar datos requeridos
        required_fields = ['producto_id', 'cantidad', 'color_seleccionado', 
                         'direccion_entrega', 'telefono', 'fecha_entrega']
        for field in required_fields:
            if field not in pedido:
                return jsonify({'error': f'Campo requerido: {field}'}), 400

        # Validar que el color seleccionado existe para el producto
        producto = db.productos.find_one({'_id': ObjectId(pedido['producto_id'])})
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404

        color_valido = False
        for filamento_id in producto.get('filamentos', []):
            filamento = db.filamentos.find_one({'_id': filamento_id})
            if filamento and filamento['color'] == pedido['color_seleccionado']:
                color_valido = True
                break

        if not color_valido:
            return jsonify({'error': 'Color de filamento no válido para este producto'}), 400

        # Crear el pedido
        pedido_data = {
            'cliente_id': str(current_user['_id']),
            'producto_id': pedido['producto_id'],
            'cantidad': int(pedido['cantidad']),
            'color_seleccionado': pedido['color_seleccionado'],
            'direccion_entrega': pedido['direccion_entrega'],
            'telefono': pedido['telefono'],
            'especificaciones': pedido.get('especificaciones', ''),
            'fecha_entrega': pedido['fecha_entrega'],
            'estado': 'pendiente',
            'fecha_creacion': datetime.utcnow()
        }

        resultado = db.pedidos.insert_one(pedido_data)
        return jsonify({
            "mensaje": "Pedido creado exitosamente",
            "id": str(resultado.inserted_id)
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pedidos/<pedido_id>/estado', methods=['PUT'])
@token_required
def actualizar_estado_pedido(current_user, pedido_id):
    try:
        print(f"Iniciando actualización de estado para pedido: {pedido_id}")
        data = request.get_json()
        nuevo_estado = data.get('estado')
        
        if not nuevo_estado:
            return jsonify({'error': 'No se proporcionó un nuevo estado'}), 400
            
        print(f"Nuevo estado: {nuevo_estado}")
        
        # Obtener el pedido actual
        pedido = db.pedidos.find_one({'_id': ObjectId(pedido_id)})
        if not pedido:
            print(f"Pedido no encontrado: {pedido_id}")
            return jsonify({'error': 'Pedido no encontrado'}), 404
            
        print(f"Pedido encontrado: {pedido}")
        
        # Si el nuevo estado es 'en_proceso', reducir el stock del filamento seleccionado
        if nuevo_estado == 'en_proceso':
            print("Procesando reducción de stock...")
            # Obtener el producto asociado al pedido
            producto = db.productos.find_one({'_id': ObjectId(pedido['producto_id'])})
            if not producto:
                print(f"Producto no encontrado para pedido: {pedido_id}")
                return jsonify({'error': 'Producto no encontrado'}), 404
                
            print(f"Producto encontrado: {producto}")
            
            # Obtener el color seleccionado del pedido
            color_seleccionado = pedido.get('color_seleccionado')
            if not color_seleccionado:
                return jsonify({'error': 'No se especificó el color del filamento'}), 400

            # Buscar el filamento con el color seleccionado
            filamento_encontrado = None
            for filamento_id in producto.get('filamentos', []):
                filamento = db.filamentos.find_one({'_id': filamento_id})
                if filamento and filamento['color'] == color_seleccionado:
                    filamento_encontrado = filamento
                    break

            if not filamento_encontrado:
                return jsonify({'error': f'No se encontró el filamento de color {color_seleccionado}'}), 404

            # Verificar y actualizar el stock del filamento seleccionado
            try:
                stock_actual = int(str(filamento_encontrado.get('stock', '0')).replace(',', ''))
                cantidad_pedido = int(pedido.get('cantidad', 0))
                
                if stock_actual < cantidad_pedido:
                    return jsonify({
                        'error': f'Stock insuficiente para el filamento {color_seleccionado}',
                        'stock_actual': stock_actual,
                        'cantidad_necesaria': cantidad_pedido
                    }), 400
                    
                # Actualizar el stock del filamento seleccionado
                nuevo_stock = stock_actual - cantidad_pedido
                resultado = db.filamentos.update_one(
                    {'_id': filamento_encontrado['_id']},
                    {'$set': {'stock': nuevo_stock}}
                )
                print(f"Stock actualizado para filamento {color_seleccionado}: {nuevo_stock}")
                
            except Exception as e:
                print(f"Error actualizando stock de filamento: {e}")
                return jsonify({'error': f'Error actualizando stock: {str(e)}'}), 500
        
        # Actualizar el estado del pedido
        try:
            resultado = db.pedidos.update_one(
                {'_id': ObjectId(pedido_id)},
                {'$set': {'estado': nuevo_estado}}
            )
            
            if resultado.modified_count == 0:
                print("No se pudo actualizar el estado del pedido")
                return jsonify({'error': 'No se pudo actualizar el estado del pedido'}), 400
                
            print(f"Estado del pedido actualizado a: {nuevo_estado}")
            return jsonify({'mensaje': 'Estado actualizado correctamente'})
            
        except Exception as e:
            print(f"Error actualizando estado del pedido: {e}")
            return jsonify({'error': f'Error actualizando estado: {str(e)}'}), 500
            
    except Exception as e:
        print(f"Error general en actualizar_estado_pedido: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/pedidos/<pedido_id>', methods=['DELETE'])
@token_required
def eliminar_pedido(current_user, pedido_id):
    if not current_user.get('is_admin', False):
        return jsonify({'error': 'No autorizado'}), 403
        
    try:
        # Verificar si el pedido existe
        pedido = db.pedidos.find_one({'_id': ObjectId(pedido_id)})
        if not pedido:
            return jsonify({'error': 'Pedido no encontrado'}), 404
            
        # Eliminar el pedido
        resultado = db.pedidos.delete_one({'_id': ObjectId(pedido_id)})
        
        if resultado.deleted_count == 0:
            return jsonify({'error': 'No se pudo eliminar el pedido'}), 400
            
        return jsonify({'mensaje': 'Pedido eliminado correctamente'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rutas para Categorías
@app.route('/categorias', methods=['GET', 'OPTIONS'])
@token_required
def get_categorias(current_user):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        categorias = list(db.categorias.find())
        for categoria in categorias:
            categoria['_id'] = str(categoria['_id'])
        return jsonify(categorias)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/categorias', methods=['POST', 'OPTIONS'])
@token_required
def crear_categoria(current_user):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        categoria = request.json
        resultado = db.categorias.insert_one(categoria)
        return jsonify({"mensaje": "Categoría creada", "id": str(resultado.inserted_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/categorias/<categoria_id>', methods=['PUT', 'OPTIONS'])
@token_required
def actualizar_categoria(current_user, categoria_id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        categoria = request.json
        resultado = db.categorias.update_one(
            {'_id': ObjectId(categoria_id)},
            {'$set': categoria}
        )
        if resultado.modified_count == 0:
            return jsonify({"error": "Categoría no encontrada"}), 404
        return jsonify({"mensaje": "Categoría actualizada correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/categorias/<categoria_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def eliminar_categoria(current_user, categoria_id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        # Verificar si hay productos asociados a esta categoría
        productos = db.productos.find_one({'categoria': categoria_id})
        if productos:
            return jsonify({"error": "No se puede eliminar la categoría porque tiene productos asociados"}), 400

        resultado = db.categorias.delete_one({'_id': ObjectId(categoria_id)})
        if resultado.deleted_count == 0:
            return jsonify({"error": "Categoría no encontrada"}), 404
        return jsonify({"mensaje": "Categoría eliminada correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.json
        
        # Verificar que todos los campos requeridos estén presentes
        required_fields = ['nombre', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'mensaje': f'El campo {field} es requerido'}), 400
        
        # Verificar si el email ya está registrado
        if db.users.find_one({'email': data['email']}):
            return jsonify({'mensaje': 'El email ya está registrado'}), 400
        
        # Crear nuevo usuario
        nuevo_usuario = {
            'nombre': data['nombre'],
            'email': data['email'],
            'password': data['password'],  # En producción, usar hash de contraseña
            'is_admin': False  # Por defecto, todos los registros son usuarios normales
        }
        
        resultado = db.users.insert_one(nuevo_usuario)
        
        return jsonify({
            'mensaje': 'Usuario registrado exitosamente',
            'id': str(resultado.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({'mensaje': str(e)}), 500

@app.route('/')
def home():
    return jsonify({"message": "API funcionando correctamente"})

@app.route('/test-db')
def test_db():
    try:
        # Intentar una operación simple
        result = db.test.insert_one({"test": "conexión"})
        return jsonify({"message": "Conexión a la base de datos exitosa", "id": str(result.inserted_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rutas para Filamentos
@app.route('/filamentos', methods=['GET', 'OPTIONS'])
@token_required
def get_filamentos(current_user):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        filamentos = list(db.filamentos.find())
        for filamento in filamentos:
            filamento['_id'] = str(filamento['_id'])
        return jsonify(filamentos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/filamentos', methods=['POST', 'OPTIONS'])
@token_required
def crear_filamento(current_user):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        filamento = request.json
        resultado = db.filamentos.insert_one(filamento)
        return jsonify({"mensaje": "Filamento creado", "id": str(resultado.inserted_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/filamentos/<filamento_id>', methods=['PUT', 'OPTIONS'])
@token_required
def actualizar_filamento(current_user, filamento_id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        filamento = request.json
        resultado = db.filamentos.update_one(
            {'_id': ObjectId(filamento_id)},
            {'$set': filamento}
        )
        if resultado.modified_count == 0:
            return jsonify({"error": "Filamento no encontrado"}), 404
        return jsonify({"mensaje": "Filamento actualizado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/filamentos/<filamento_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def eliminar_filamento(current_user, filamento_id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        # Verificar si hay productos que usan este filamento
        productos = db.productos.find_one({'filamentos': filamento_id})
        if productos:
            return jsonify({"error": "No se puede eliminar el filamento porque está siendo usado en productos"}), 400

        resultado = db.filamentos.delete_one({'_id': ObjectId(filamento_id)})
        if resultado.deleted_count == 0:
            return jsonify({"error": "Filamento no encontrado"}), 404
        return jsonify({"mensaje": "Filamento eliminado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pedidos/flujo/<fecha>', methods=['GET'])
@token_required
def analizar_flujo_pedidos(current_user, fecha):
    if not current_user.get('is_admin', False):
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        pedido_flow = PedidoFlow()
        reporte = pedido_flow.generar_reporte(fecha)
        
        if reporte is None:
            return jsonify({'error': 'Error al generar el reporte'}), 500
            
        return jsonify(reporte)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sugerencias', methods=['GET'])
@token_required
def obtener_sugerencias(current_user):
    if not current_user.get('is_admin', False):
        return jsonify({'error': 'No autorizado'}), 403
        
    try:
        sugerencias_flow = SugerenciasFlow()
        reporte = sugerencias_flow.generar_reporte_sugerencias()
        
        if reporte is None:
            return jsonify({'error': 'Error al generar sugerencias'}), 500
            
        return jsonify(reporte)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def asegurar_stock_numerico():
    """
    Asegura que todos los filamentos tengan su stock como número
    """
    try:
        filamentos = db.filamentos.find({})
        for filamento in filamentos:
            stock_actual = filamento.get('stock')
            if isinstance(stock_actual, str):
                # Convertir a número
                nuevo_stock = int(str(stock_actual).replace(',', ''))
                db.filamentos.update_one(
                    {'_id': filamento['_id']},
                    {'$set': {'stock': nuevo_stock}}
                )
                print(f"Stock actualizado para filamento {filamento['_id']}: {nuevo_stock}")
    except Exception as e:
        print(f"Error asegurando stock numérico: {e}")

# Llamar a la función al iniciar la aplicación
asegurar_stock_numerico()

if __name__ == '__main__':
    try:
        app.run(debug=True, host='127.0.0.1', port=5000)
    except KeyboardInterrupt:
        print("\nCerrando servidor...")
    except Exception as e:
        print(f"Error al iniciar el servidor: {e}")
    finally:
        # Cerrar la conexión a MongoDB
        if 'client' in locals():
            client.close()
            print("Conexión a MongoDB cerrada") 