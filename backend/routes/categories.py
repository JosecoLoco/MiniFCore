from flask import Blueprint, request, jsonify
from models.category import Category
from models.mongo import mongo
from routes.auth import token_required
from bson import ObjectId

categories = Blueprint('categories', __name__)

@categories.route('/', methods=['GET'])
def get_categories():
    categories_data = list(mongo.db.categories.find())
    return jsonify([{
        **category,
        '_id': str(category['_id'])
    } for category in categories_data])

@categories.route('/<category_id>', methods=['GET'])
def get_category(category_id):
    category = mongo.db.categories.find_one({'_id': ObjectId(category_id)})
    if not category:
        return jsonify({'message': 'Categoría no encontrada'}), 404
    
    category['_id'] = str(category['_id'])
    return jsonify(category)

@categories.route('/', methods=['POST'])
@token_required
def create_category(current_user):
    if not current_user.get('is_admin'):
        return jsonify({'message': 'No autorizado'}), 403
    
    data = request.get_json()
    required_fields = ['name', 'description', 'icon']
    
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Faltan campos requeridos'}), 400
    
    category = Category(
        name=data['name'],
        description=data['description'],
        icon=data['icon']
    )
    
    result = mongo.db.categories.insert_one(category.to_dict())
    category_dict = category.to_dict()
    category_dict['_id'] = str(result.inserted_id)
    
    return jsonify(category_dict), 201

@categories.route('/<category_id>', methods=['PUT'])
@token_required
def update_category(current_user, category_id):
    if not current_user.get('is_admin'):
        return jsonify({'message': 'No autorizado'}), 403
    
    category = mongo.db.categories.find_one({'_id': ObjectId(category_id)})
    if not category:
        return jsonify({'message': 'Categoría no encontrada'}), 404
    
    data = request.get_json()
    category_obj = Category.from_dict(category)
    
    # Actualizar campos
    if 'name' in data:
        category_obj.name = data['name']
    if 'description' in data:
        category_obj.description = data['description']
    if 'icon' in data:
        category_obj.icon = data['icon']
    
    updated_data = category_obj.to_dict()
    mongo.db.categories.update_one(
        {'_id': ObjectId(category_id)},
        {'$set': updated_data}
    )
    
    updated_data['_id'] = str(category_id)
    return jsonify(updated_data)

@categories.route('/<category_id>', methods=['DELETE'])
@token_required
def delete_category(current_user, category_id):
    if not current_user.get('is_admin'):
        return jsonify({'message': 'No autorizado'}), 403
    
    result = mongo.db.categories.delete_one({'_id': ObjectId(category_id)})
    if result.deleted_count == 0:
        return jsonify({'message': 'Categoría no encontrada'}), 404
    
    return jsonify({'message': 'Categoría eliminada exitosamente'}) 