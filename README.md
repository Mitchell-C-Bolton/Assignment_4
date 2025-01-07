# 🛒 E-commerce API with Flask

The E-commerce API is a RESTful application built with Flask, SQLAlchemy, and MySQL. This project allows for managing users, orders, and products with robust relationships (One-to-Many and Many-to-Many) and implements Marshmallow for input validation and data serialization.

## 🔧 Features

- Full CRUD operations for users, products, and orders
- One-to-Many and Many-to-Many database relationships
- Marshmallow schemas for validation and serialization
- Error handeling to return appropriate error messages and status codes.

---

## 🛠️ Technologies Used

- **Programing Language:** Python
- **Framework:** Flask
- **ORM:** SQLAlchemy
- **Validation:** Marshmallow
- **Database:** MySQL
- **Development Environment:** Visual Studio Code

---

## 📦 API Routes

### Customers
- GET /customers: Retrieve a list of all customers.
- GET /customers/int:id: Retrieve details of a specific customer by their ID.
- POST /customers: Add a new customer to the database.
- PUT /customers/int:id: Update the details of an existing customer by their ID.
- DELETE /customers/int:id: Remove a customer from the database by their ID.

### Products
- GET /products: Retrieve a list of all products.
- GET /products/int:id: Retrieve details of a specific product by its ID.
- POST /products: Add a new product to the database.
- PUT /products/int:id: Update the details of an existing product by its ID.
- DELETE /products/int:id: Remove a product from the database by its ID.

### Orders
- GET /orders: Retrieve a list of all orders.
- GET /orders/int:id: Retrieve details of a specific order by its ID.
- GET /orders/orders_for_customer/int:customer_id: Retrieve all orders associated with a specific customer.
- POST /orders: Add a new order.
- POST /orders/int:customer_id: Create a new order for a specific customer by their ID.
- DELETE /orders/int:id: Remove an order from the database by its ID.

### Order Product Management
- POST /orders/int:order_id/add_product/int:product_id/qty/int:quantity: Add a product to a specific order with the specified quantity.
- DELETE /orders/int:order_id/remove_product/int:product_id: Remove a product from a specific order.

### Utilities
- DELETE /panic_button: Deletes the entire database. Primarily for UAT (User Acceptance Testing) purposes.
- POST /load_test_data: Load pre-defined, hard-coded test data into the database. Primarily for UAT purposes.

---

## 🚀 How to Run

1. Clone the repository:
   git clone https://github.com/YourUsername/Ecommerce-API

2. Navigate to the project directory:
   cd Ecommerce-API

3. Install the required dependencies:
   pip install -r requirements.txt

4. Run the applicaiton from the app.py file.