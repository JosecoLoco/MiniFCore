from flask import Blueprint, request, jsonify
from models.product import Product
from models.mongo import mongo
from routes.auth import token_required
from bson import ObjectId

products = Blueprint('products', __name__)

@products.route('/', methods=['GET'])
def get_products():
    category_id = request.args.get('category_id')
    query = {'category_id': category_id} if category_id else {}
    
    products_data = list(mongo.db.products.find(query))
    return jsonify([{
        **product,
        '_id': str(product['_id'])
    } for product in products_data])

@products.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    product = mongo.db.products.find_one({'_id': ObjectId(product_id)})
    if not product:
        return jsonify({'message': 'Producto no encontrado'}), 404
    
    product['_id'] = str(product['_id'])
    return jsonify(product)

@products.route('/', methods=['POST'])
@token_required
def create_product(current_user):
    if not current_user.get('is_admin'):
        return jsonify({'message': 'No autorizado'}), 403
    
    data = request.get_json()
    required_fields = ['name', 'description', 'price', 'category_id', 'material', 'print_time']
    
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Faltan campos requeridos'}), 400
    
    product = Product(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        category_id=data['category_id'],
        material=data['material'],
        print_time=data['print_time'],
        images=data.get('images', [])
    )
    
    result = mongo.db.products.insert_one(product.to_dict())
    product_dict = product.to_dict()
    product_dict['_id'] = str(result.inserted_id)
    
    return jsonify(product_dict), 201

@products.route('/<product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):
    if not current_user.get('is_admin'):
        return jsonify({'message': 'No autorizado'}), 403
    
    product = mongo.db.products.find_one({'_id': ObjectId(product_id)})
    if not product:
        return jsonify({'message': 'Producto no encontrado'}), 404
    
    data = request.get_json()
    product_obj = Product.from_dict(product)
    updated_data = product_obj.update(data)
    
    mongo.db.products.update_one(
        {'_id': ObjectId(product_id)},
        {'$set': updated_data}
    )
    
    updated_data['_id'] = str(product_id)
    return jsonify(updated_data)

@products.route('/<product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    if not current_user.get('is_admin'):
        return jsonify({'message': 'No autorizado'}), 403
    
    result = mongo.db.products.delete_one({'_id': ObjectId(product_id)})
    if result.deleted_count == 0:
        return jsonify({'message': 'Producto no encontrado'}), 404
    
    return jsonify({'message': 'Producto eliminado exitosamente'}) 