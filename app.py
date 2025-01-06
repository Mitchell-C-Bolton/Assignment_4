# Imports ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from datetime import datetime
from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
from sqlalchemy import DECIMAL, Column, ForeignKey, Integer, String, Table, delete, func, select
import sqlalchemy
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

order_product = Table(
    'order_product',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('order_id', ForeignKey('orders.id')),
    Column('product_id', ForeignKey('products.id')),
    Column('quantity', Integer, nullable=False, default=1)
)

class Customer(Base):
    __tablename__ = 'customers'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    address: Mapped[str] = mapped_column(String(300))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    
    # One to many relationship with orders
    orders: Mapped[List['Order']] = relationship(back_populates='customers')
    
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
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'))
    
    # Many to one relationship with customer
    customers: Mapped['Customer'] = relationship(back_populates='orders')
    
    
# Marshmallow Schemas ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        include_relationships = True

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
        include_relationships = True
        
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

# Customer End Points ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.route('/customers/<int:id>', 
    methods=['GET']) # Read customer
def read_customer(id):
    customer = db.session.get(Customer, id)
    
    if not customer:
        return jsonify({"ERROR": f"Invalid customer ID: {id}"}), 400
    
    return customer_schema.jsonify(customer), 200

@app.route('/customers', 
    methods=['GET']) # Read all customers
def read_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()
    
    return customers_schema.jsonify(customers), 200

@app.route('/customers', 
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

@app.route('/customers/<int:id>', 
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

@app.route('/customers/<int:id>', 
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

# Product End Points ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.route('/products/<int:id>', 
    methods=['GET']) # Read product
def read_product(id):
    product = db.session.get(Product, id)
    
    if not product:
        return jsonify({"ERROR": f"Invalid product ID: {id}"}), 400
    
    return product_schema.jsonify(product), 200

@app.route('/products', methods=['GET']) # Read all products
def read_products():
    query = select(Product)
    products = db.session.execute(query).scalars().all()
    
    return products_schema.jsonify(products), 200

@app.route('/products', 
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

@app.route('/products/<int:id>', 
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

@app.route('/products/<int:id>', 
    methods=['DELETE']) # Delete product
def delete_product(id):
    product = db.session.get(Product, id)
     
    if not product:
        return jsonify({"ERROR": f"Invalid product ID: {id}"}), 400
    
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({"message": f"Product {id} was deleted"}), 200

# Order End Points ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.route('/orders/<int:id>', 
    methods=['GET']) # Read order
def read_order(id):
    order = db.session.get(Order, id)
    
    if not order:
        return jsonify({"ERROR": f"Invalid order ID: {id}"}), 400
    
    return order_schema.jsonify(order), 200

@app.route('/orders', 
    methods=['GET']) # Read all orders
def read_orders():
    query = select(Order)
    orders = db.session.execute(query).scalars().all()
    
    return orders_schema.jsonify(orders), 200

@app.route('/orders/orders_for_customer/<int:customer_id>',
        methods=['GET']) # Read all orders for a customer
def read_all_orders_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({"ERROR": f"Invalid customer ID: {customer_id}"}), 400
    else:
        query = select(Order).where(Order.customer_id == customer_id)
        orders = db.session.execute(query).scalars().all()
        
        return orders_schema.jsonify(orders), 200

@app.route('/orders/<int:customer_id>', 
    methods=['POST']) # Write order
def create_order(customer_id):
    new_order = Order(customer_id=customer_id)

    db.session.add(new_order)
    db.session.commit()
    
    return order_schema.jsonify(new_order), 201

# Update order seemed irrelevant
# will add if order table gets any content worth updating. 

@app.route('/orders/<int:id>', 
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

# Order Product Relation End Points ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.route('/orders/<int:order_id>/add_product/<int:product_id>/qty/<int:quantity>', 
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
    
@app.route('/orders/<int:order_id>/remove_product/<int:product_id>', 
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

# Other Database Commands ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.route('/panic_button',
    methods=['DELETE']) # Deletes the entire database (UAT purposes)
def Delete_database():
    db.drop_all()
    db.create_all()
    db.session.commit()
    return jsonify({"message": "Clean slate protocol complete."}), 200

@app.route('/load_test_data', 
    methods=['POST']) # Loads a lot of hard coded data (UAT purposes)
def load_test_data():
    
    try:
        mitchell = Customer( # Create customers
            name='Mitchell', 
            address='12345 test Ave NE',
            email='mitchellishere@gmail.com'
            )
        sabrina = Customer(
            name='Sabrina', 
            address='1324 Very Fast Ln S',
            email='coolcatsabrina@aol.com'
            )
        jake = Customer(
            name='Jake', 
            address='9876 Tutle St N',
            email='jakethesnake@outlook.com'
            )
        
        shoes = Product( # Create products
            name='shoes',
            price=29.99
        )
        shirt = Product(
            name='shirt',
            price=19.99
        )
        jacket = Product(
            name='jacket',
            price=58.99
        )
        
        order1 = Order( # Create orders
            customer_id=1
        )
        order2 = Order(
            customer_id=1
        )
        order3 = Order(
            customer_id=1
        )
        order4 = Order(
            customer_id=2
        )
        order5 = Order(
            customer_id=2
        )
        order6 = Order( # Intentionally empty order
            customer_id=3
        )
        
        db.session.add(mitchell)
        db.session.add(sabrina)
        db.session.add(jake)
        db.session.add(shoes)
        db.session.add(shirt)
        db.session.add(jacket)
        db.session.add(order1)
        db.session.add(order2)
        db.session.add(order3)
        db.session.add(order4)
        db.session.add(order5)
        db.session.add(order6)

        db.session.commit()
        
        db.session.execute( # Create order-product relationships
            order_product.insert().values(
                order_id=1,
                product_id=1,
                quantity=1
            )
        )
        db.session.execute(
            order_product.insert().values(
                order_id=1,
                product_id=3,
                quantity=2
            )
        )
        db.session.execute(
            order_product.insert().values(
                order_id=1,
                product_id=2,
                quantity=7
            )
        )
        db.session.execute(
            order_product.insert().values(
                order_id=2,
                product_id=2,
                quantity=5
            )
        )
        db.session.execute(
            order_product.insert().values(
                order_id=3,
                product_id=1,
                quantity=1
            )
        )
        db.session.execute(
            order_product.insert().values(
                order_id=3,
                product_id=2,
                quantity=1
            )
        )
        db.session.execute(
            order_product.insert().values(
                order_id=3,
                product_id=3,
                quantity=1
            )
        )
        db.session.execute(
            order_product.insert().values(
                order_id=4,
                product_id=3,
                quantity=3
            )
        )
        db.session.execute(
            order_product.insert().values(
                order_id=4,
                product_id=2,
                quantity=3
            )
        )
        db.session.execute(
            order_product.insert().values(
                order_id=4,
                product_id=1,
                quantity=2
            )
        )
        db.session.execute(
            order_product.insert().values(
                order_id=5,
                product_id=2,
                quantity=6
            )
        )
        
        db.session.commit()
        
    except:
        return jsonify({"ERROR": "Test data failed to load. Try clearing all existing data first."}), 400
    return jsonify({"message": "Test data has been loaded into database"}), 200

# Run App ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ ==  '__main__':
    with app.app_context():
        db.create_all()
        
    app.run(debug=True)