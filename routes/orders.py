# Imports ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select, delete
import sqlalchemy
from models import db, Customer, Order, Product, order_product
from schemas import order_schema, orders_schema

# Main ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

order_bp = Blueprint('orders', __name__)

@order_bp.route('/orders/<int:id>', 
    methods=['GET']) # Read order
def read_order(id):
    order = db.session.get(Order, id)
    
    if not order:
        return jsonify({"ERROR": f"Invalid order ID: {id}"}), 400
    
    return order_schema.jsonify(order), 200

@order_bp.route('/orders', 
    methods=['GET']) # Read all orders
def read_orders():
    query = select(Order)
    orders = db.session.execute(query).scalars().all()
    
    return orders_schema.jsonify(orders), 200

@order_bp.route('/orders/orders_for_customer/<int:customer_id>',
        methods=['GET']) # Read all orders for a customer
def read_all_orders_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({"ERROR": f"Invalid customer ID: {customer_id}"}), 400
    else:
        query = select(Order).where(Order.customer_id == customer_id)
        orders = db.session.execute(query).scalars().all()
        
        return orders_schema.jsonify(orders), 200

@order_bp.route('/orders/<int:customer_id>', 
    methods=['POST']) # Write order
def create_order(customer_id):
    new_order = Order(customer_id=customer_id)

    db.session.add(new_order)
    db.session.commit()
    
    return order_schema.jsonify(new_order), 201

# Update order seemed irrelevant
# will add if order table gets any content worth updating. 

@order_bp.route('/orders/<int:id>', 
    methods=['DELETE']) # Delete order
def delete_order(id):
    order = db.session.get(Order, id)
    
    if not order:
        return jsonify({"ERROR": f"Invalid order ID: {id}"}), 400
    
    db.session.execute( # Deletes all associations between the order and the product.
        delete(order_product).where(
            order_product.c.order_id == id))
    
    db.session.delete(order)
    db.session.commit()
    
    return jsonify({"message": f"Order {id} was deleted"}), 200