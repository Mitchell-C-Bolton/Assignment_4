# models.py
# Imports ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from datetime import datetime
from sqlalchemy import DECIMAL, Column, ForeignKey, Integer, String, Table, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List
from flask_sqlalchemy import SQLAlchemy

# Main ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

order_product = Table( # Relationshipo table between order and product tables
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
    # Price rounds to nearest second decimal place 5^ and 4v 5.995 = 6.0
    price: Mapped[float] = mapped_column(DECIMAL(precision=10, scale=2))
    
class Order(Base):
    __tablename__ = 'orders'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    order_create_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'))
    
    # Many to one relationship with customer
    customers: Mapped['Customer'] = relationship(back_populates='orders')