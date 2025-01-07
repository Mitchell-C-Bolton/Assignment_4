# Imports ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from flask import Blueprint, jsonify
from models import db, Customer, Order, Product, order_product

# Main ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

utility_bp = Blueprint('utilities', __name__)

@utility_bp.route('/panic_button',
    methods=['DELETE']) # Deletes the entire database (UAT purposes)
def Delete_database():
    db.drop_all()
    db.create_all()
    db.session.commit()
    return jsonify({"message": "Clean slate protocol complete."}), 200

@utility_bp.route('/load_test_data', 
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