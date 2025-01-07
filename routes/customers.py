# Imports ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select, delete
import sqlalchemy
from models import db, Customer, Order, order_product
from schemas import customer_schema, customers_schema

# Main ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

customer_bp = Blueprint('customers', __name__)

@customer_bp.route('/customers/<int:id>', 
    methods=['GET']) # Read customer
def read_customer(id):
    customer = db.session.get(Customer, id)
    
    if not customer:
        return jsonify({"ERROR": f"Invalid customer ID: {id}"}), 400
    
    return customer_schema.jsonify(customer), 200

@customer_bp.route('/customers', 
    methods=['GET']) # Read all customers
def read_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()
    
    return customers_schema.jsonify(customers), 200

@customer_bp.route('/customers', 
    methods=['POST']) # Write customer
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400
    
    new_customer = Customer(
        name=customer_data['name'], 
        address=customer_data['address'],
        email=customer_data['email']
        )
    try:
        db.session.add(new_customer)
        db.session.commit()
        return customer_schema.jsonify(new_customer), 201
    
    except sqlalchemy.exc.IntegrityError:
        return jsonify({"ERROR": 
            f"{new_customer.email} is most likely tied to another user."}), 400

@customer_bp.route('/customers/<int:id>', 
    methods=['PUT']) # Update customer
def update_customer(id):
    customer = db.session.get(Customer, id)
    
    if not customer:
        return jsonify({"ERROR": f"Invalid customer ID: {id}"}), 400
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer.name = customer_data['name']
    customer.address = customer_data['address']
    customer.email = customer_data['email']
    
    db.session.commit()
    return customer_schema.jsonify(customer), 200

@customer_bp.route('/customers/<int:id>', 
    methods=['DELETE']) # Delete customer
def delete_customer(id):
    customer = db.session.get(Customer, id)
    
    db.session.execute( # Deletes all order_products associated with the order associated with the customer
        delete(order_product).where(order_product.c.order_id.in_(
            select(Order.id).where(Order.customer_id == id)
        ))
    )
    
    db.session.execute( # Deletes all orders associated with the customer
        delete(Order).where(Order.customer_id == id)
        )
    
    if not customer:
        return jsonify({"ERROR": f"Invalid customer ID: {id}"}), 400

    else:
        db.session.delete(customer)
        db.session.commit()
    
        return jsonify({"message": f"Cusomer {id} was deleted"}), 200