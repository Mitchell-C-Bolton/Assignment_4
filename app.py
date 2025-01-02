# Imports ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from datetime import datetime
from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
from sqlalchemy import DECIMAL, Column, ForeignKey, Integer, String, Table, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List

# Flask/SQL Setup ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql+mysqlconnector://root:code1234camp@localhost/ecommerce_api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)

# SQL Tables ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Customer(Base):
    __tablename__ = 'customers'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    address: Mapped[str] = mapped_column(String(300))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    
    # One to many relationship with orders
    orders: Mapped[List['Order']] = relationship(back_populates='customers', cascade="all, delete-orphan")
    
class Product(Base):
    __tablename__ = 'products'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(300))
    # Price rounds to nearest second decimial place 5^ and 4v 5.995 = 6.0
    price: Mapped[float] = mapped_column(DECIMAL(precision=10, scale=2))
    
class Order(Base):
    __tablename__ = 'orders'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    order_create_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey('customers.id'))
    
    # Many to one relationship with customer
    customers: Mapped['Customer'] = relationship(back_populates='orders')
    
order_product = Table(
    'order_product',
    Base.metadata,
    Column('order_id', ForeignKey('orders.id')),
    Column('product_id', ForeignKey('products.id')),
    Column('quantity', Integer, nullable=False, default=1)
)
    
# Marshmallow Schemas ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

# User End Points ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.route('/customers', methods=['POST']) # Write customer
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

    db.session.add(new_customer)
    db.session.commit()
    
    return customer_schema.jsonify(new_customer), 201

@app.route('/customers/<int:id>', methods=['GET']) # Read customer
def read_customer(id):
    customer = db.session.get(Customer, id)
    
    if not customer:
        return jsonify({"message": f"Invalid customer ID: {id}"}), 400
    
    return customer_schema.jsonify(customer), 200

@app.route('/customers', methods=['GET']) # Read all customers
def read_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()
    
    return customers_schema.jsonify(customers), 200

@app.route('/customers/<int:id>', methods=['DELETE']) # Delete customer
def delete_customer(id):
    customer = db.session.get(Customer, id)
     
    if not customer:
        return jsonify({"message": f"Invalid customer ID: {id}"}), 400
    
    db.session.delete(customer)
    db.session.commit()
    
    return jsonify({"message": f"User {id} was deleted"}), 200

# Product End Points ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.route('/products', methods=['POST']) # Write product
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
    
    return product_schema.jsonify(new_product), 201

@app.route('/products/<int:id>', methods=['GET']) # Read product
def read_product(id):
    product = db.session.get(Product, id)
    
    if not product:
        return jsonify({"message": f"Invalid product ID: {id}"}), 400
    
    return customer_schema.jsonify(product), 200

@app.route('/products', methods=['GET']) # Read all products
def read_products():
    query = select(Product)
    products = db.session.execute(query).scalars().all()
    
    return customers_schema.jsonify(products), 200

@app.route('/products/<int:id>', methods=['DELETE']) # Delete product
def delete_product(id):
    product = db.session.get(Product, id)
     
    if not product:
        return jsonify({"message": f"Invalid product ID: {id}"}), 400
    
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({"message": f"Product {id} was deleted"}), 200

# Order End Points ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.route('/orders/<int:user_id>', methods=['POST']) # Write order
def create_order(user_id):
    
    new_order = Order(user_id=user_id)

    db.session.add(new_order)
    db.session.commit()
    
    return product_schema.jsonify(new_order), 201

@app.route('/orders/<int:id>', methods=['GET']) # Read order
def read_order(id):
    order = db.session.get(Order, id)
    
    if not order:
        return jsonify({"message": f"Invalid order ID: {id}"}), 400
    
    return order_schema.jsonify(order), 200

@app.route('/orders', methods=['GET']) # Read all orders
def read_orders():
    query = select(Order)
    orders = db.session.execute(query).scalars().all()
    
    return orders_schema.jsonify(orders), 200

@app.route('/orders/<int:id>', methods=['DELETE']) # Delete order
def delete_order(id):
    order = db.session.get(Order, id)
     
    if not order:
        return jsonify({"message": f"Invalid order ID: {id}"}), 400
    
    db.session.delete(order)
    db.session.commit()
    
    return jsonify({"message": f"Order {id} was deleted"}), 200

# Run App ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ ==  '__main__':
    with app.app_context():
        db.create_all()
        
    app.run(debug=True)