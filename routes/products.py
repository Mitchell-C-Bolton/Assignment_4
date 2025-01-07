# Imports ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select, delete
from models import db, Product, order_product
from schemas import products_schema, product_schema

# Main ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

product_bp = Blueprint('products', __name__)

@product_bp.route('/products/<int:id>', 
    methods=['GET']) # Read product
def read_product(id):
    product = db.session.get(Product, id)
    
    if not product:
        return jsonify({"ERROR": f"Invalid product ID: {id}"}), 400
    
    return product_schema.jsonify(product), 200

@product_bp.route('/products', methods=['GET']) # Read all products
def read_products():
    query = select(Product)
    products = db.session.execute(query).scalars().all()
    
    return products_schema.jsonify(products), 200

@product_bp.route('/products', 
    methods=['POST']) # Write product
def create_product():
    try:
        product_data = product_schema.load(request.json)
        product_data['price'] = round(float(product_data['price']), 2)
    except ValidationError as error:
        return jsonify(error.messages), 400
    
    new_product = Product(
        name=product_data['name'], 
        price=product_data['price']
        )

    db.session.add(new_product)
    db.session.commit()
    print(new_product.price)
    
    return product_schema.jsonify(new_product), 201

@product_bp.route('/products/<int:id>', 
    methods=['PUT']) # Update product
def update_product(id):
    product = db.session.get(Product, id)
    
    if not product:
        return jsonify({"ERROR": f"Invalid product ID: {id}"}), 400
    
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    product.name = product_data['name']
    product.price = product_data['price']
    
    db.session.commit()
    return product_schema.jsonify(product), 200

@product_bp.route('/products/<int:id>', 
    methods=['DELETE']) # Delete product
def delete_product(id):
    product = db.session.get(Product, id)
     
    if not product:
        return jsonify({"ERROR": f"Invalid product ID: {id}"}), 400
    
    db.session.execute( # Deletes all associations between the order and the product.
        delete(order_product).where(
            order_product.c.product_id == id))
    
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({"message": f"Product {id} was deleted"}), 200
