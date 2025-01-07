# Imports ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from flask import Flask
from models import db
from schemas import ma
from routes.customers import customer_bp
from routes.products import product_bp
from routes.orders import order_bp
from routes.utilities import utility_bp
from routes.orders_products import order_product_bp

# Main ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql+mysqlconnector://root:code1234camp@localhost/ecommerce_api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
ma.init_app(app)  # Initialize Marshmallow instance in app.py

app.register_blueprint(customer_bp)
app.register_blueprint(product_bp)
app.register_blueprint(order_bp)
app.register_blueprint(utility_bp)
app.register_blueprint(order_product_bp)

if __name__ ==  '__main__':
    with app.app_context():
        db.create_all()
        
    app.run(debug=True)