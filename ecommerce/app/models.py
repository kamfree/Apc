from datetime import datetime
from decimal import Decimal
from typing import Optional
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager


ROLE_CUSTOMER = "customer"
ROLE_VENDOR = "vendor"
ROLE_ADMIN = "admin"

ORDER_STATUS_PENDING = "Pending"
ORDER_STATUS_PROCESSING = "Processing"
ORDER_STATUS_SHIPPED = "Shipped"
ORDER_STATUS_DELIVERED = "Delivered"
ORDER_STATUS_CANCELLED = "Cancelled"
ORDER_STATUSES = [
    ORDER_STATUS_PENDING,
    ORDER_STATUS_PROCESSING,
    ORDER_STATUS_SHIPPED,
    ORDER_STATUS_DELIVERED,
    ORDER_STATUS_CANCELLED,
]


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(20), default=ROLE_CUSTOMER, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vendor = db.relationship("Vendor", back_populates="user", uselist=False)
    orders = db.relationship("Order", back_populates="user")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_id(self) -> str:
        return str(self.id)

    @property
    def is_admin(self) -> bool:
        return self.role == ROLE_ADMIN

    @property
    def is_vendor(self) -> bool:
        return self.role == ROLE_VENDOR


@login_manager.user_loader
def load_user(user_id: str) -> Optional["User"]:
    return User.query.get(int(user_id))


class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    approved = db.Column(db.Boolean, default=False)

    user = db.relationship("User", back_populates="vendor")
    products = db.relationship("Product", back_populates="vendor")


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)

    parent = db.relationship("Category", remote_side=[id], backref="children")
    products = db.relationship("Product", back_populates="category")


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    image_url = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vendor = db.relationship("Vendor", back_populates="products")
    category = db.relationship("Category", back_populates="products")


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, index=True)
    session_id = db.Column(db.String(128), nullable=True, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product")


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(20), default=ORDER_STATUS_PENDING, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    shipping_name = db.Column(db.String(120), nullable=False)
    shipping_address = db.Column(db.String(255), nullable=False)
    shipping_city = db.Column(db.String(120), nullable=False)
    shipping_postal_code = db.Column(db.String(20), nullable=False)
    shipping_country = db.Column(db.String(120), nullable=False)

    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    user = db.relationship("User", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def compute_total(self) -> Decimal:
        total = Decimal("0.00")
        for item in self.items:
            total += item.unit_price * item.quantity
        self.total_amount = total
        return total


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product")