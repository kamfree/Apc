from .extensions import db
from .models import User, Vendor, Category, Product, ROLE_ADMIN, ROLE_VENDOR, ROLE_CUSTOMER
from flask import current_app


def seed_data_if_needed() -> None:
    if User.query.first():
        return

    # Create Admin
    admin_email = current_app.config.get("ADMIN_EMAIL", "admin@example.com")
    admin = User(email=admin_email, name="Admin", role=ROLE_ADMIN)
    admin.set_password("password")
    db.session.add(admin)

    # Create Vendor User
    vendor_user = User(email="vendor@example.com", name="Vendor User", role=ROLE_VENDOR)
    vendor_user.set_password("password")
    db.session.add(vendor_user)
    db.session.flush()

    # Create Vendor
    vendor = Vendor(user_id=vendor_user.id, name="Acme Shop", approved=True)
    db.session.add(vendor)

    # Create Customer
    customer = User(email="customer@example.com", name="John Customer", role=ROLE_CUSTOMER)
    customer.set_password("password")
    db.session.add(customer)

    # Categories
    electronics = Category(name="Electronics")
    books = Category(name="Books")
    clothing = Category(name="Clothing")
    db.session.add_all([electronics, books, clothing])
    db.session.flush()

    # Products
    products = [
        Product(vendor=vendor, category=electronics, title="Smartphone X", description="A powerful smartphone.", price=699.99, stock=25, image_url="https://via.placeholder.com/300x200?text=Phone"),
        Product(vendor=vendor, category=electronics, title="Noise Cancelling Headphones", description="Immersive sound.", price=199.99, stock=40, image_url="https://via.placeholder.com/300x200?text=Headphones"),
        Product(vendor=vendor, category=books, title="Flask Web Development", description="Learn Flask.", price=39.99, stock=100, image_url="https://via.placeholder.com/300x200?text=Book"),
        Product(vendor=vendor, category=clothing, title="Classic T-Shirt", description="100% cotton.", price=14.99, stock=200, image_url="https://via.placeholder.com/300x200?text=T-Shirt"),
    ]
    db.session.add_all(products)

    db.session.commit()