# Imports ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from flask import Blueprint, jsonify
from sqlalchemy import select, delete
from models import Product, db, Order, order_product

# Main ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

order_product_bp = Blueprint('orders_products', __name__)

@order_product_bp.route('/orders/<int:order_id>/add_product/<int:product_id>/qty/<int:quantity>', 
           methods=['POST']) # Assign a product to an order
def assign_product_to_order(product_id, order_id, quantity):
    product = db.session.get(Product, product_id)
    order = db.session.get(Order, order_id)
    
    if not product:
        return jsonify({"ERROR": f"Invalid product ID: {product_id}"}), 400
    elif not order:
        return jsonify({"ERROR": f"Invalid order ID: {order_id}"}), 400
    
    exist_check = db.session.execute( # Checks for existing order-product relations
        select(order_product).where(
            order_product.c.order_id == order_id,
            order_product.c.product_id == product_id
        )
    ).fetchone()
    
    if exist_check:
        return jsonify({"ERROR": 
        f"Relation between {product_id} and {order_id} already exists"}), 400
    else:
        db.session.execute(
            order_product.insert().values(
                order_id=order_id,
                product_id=product_id,
                quantity=quantity
            )
        )
    
    db.session.commit()
    return jsonify({"message": 
    f"{quantity} of product {product_id} has been assigned to order {order_id}."}), 200
    
@order_product_bp.route('/orders/<int:order_id>/remove_product/<int:product_id>', 
        methods=['DELETE']) # Delete a product from an order
def delete_product_from_order(order_id, product_id):
    product = db.session.get(Product, product_id)
    order = db.session.get(Order, order_id)
    
    if not product:
        return jsonify({"ERROR": f"Invalid product ID: {product_id}"}), 400
    elif not order:
        return jsonify({"ERROR": f"Invalid order ID: {order_id}"}), 400
    
    exist_check = db.session.execute( # Checks for existing order-product relations
        select(order_product).where(
            order_product.c.order_id == order_id,
            order_product.c.product_id == product_id
        )
    ).fetchone()

    if exist_check:
        db.session.execute( # Delete order-product relationship
            delete(order_product).where(
                order_product.c.order_id == order_id,
                order_product.c.product_id == product_id
            )
        )
        
        db.session.commit()
        return jsonify({"message": 
        f"Product {product_id} removed from order {order_id}."}), 200
        
    else:
        return jsonify({"message": f"Order {order_id} does not include product {product_id}."}), 400
