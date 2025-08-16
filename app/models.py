from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import enum

class UserRoles(enum.Enum):
    CUSTOMER = 'customer'
    VENDOR = 'vendor'
    ADMIN = 'admin'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.Enum(UserRoles), default=UserRoles.CUSTOMER, nullable=False)

    vendor_profile = db.relationship('VendorProfile', back_populates='user', uselist=False, cascade="all, delete-orphan")
    reviews = db.relationship('Review', back_populates='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class VendorProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    shop_name = db.Column(db.String(120), index=True, unique=True)
    description = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)

    user = db.relationship('User', back_populates='vendor_profile')
    products = db.relationship('Product', back_populates='vendor', lazy='dynamic')

    def __repr__(self):
        return f'<VendorProfile {self.shop_name}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    products = db.relationship('Product', back_populates='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor_profile.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    vendor = db.relationship('VendorProfile', back_populates='products')
    category = db.relationship('Category', back_populates='products')
    images = db.relationship('ProductImage', back_populates='product', cascade="all, delete-orphan")
    skus = db.relationship('SKU', back_populates='product', cascade="all, delete-orphan")
    reviews = db.relationship('Review', back_populates='product', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Product {self.name}>'

class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    alt_text = db.Column(db.String(100))

    product = db.relationship('Product', back_populates='images')

    def __repr__(self):
        return f'<ProductImage {self.image_url}>'

class SKU(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    sku_code = db.Column(db.String(50), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)
    attributes = db.Column(db.JSON) # e.g., {'color': 'Red', 'size': 'M'}

    product = db.relationship('Product', back_populates='skus')
    inventory = db.relationship('Inventory', back_populates='sku', uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<SKU {self.sku_code}>'

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku_id = db.Column(db.Integer, db.ForeignKey('sku.id'), nullable=False, unique=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)

    sku = db.relationship('SKU', back_populates='inventory')

    def __repr__(self):
        return f'<Inventory SKU:{self.sku_id} Qty:{self.quantity}>'

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, unique=True) # A user has one cart
    session_id = db.Column(db.String(255), nullable=True, unique=True) # For guest carts
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    user = db.relationship('User')
    items = db.relationship('CartItem', back_populates='cart', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Cart {self.id}>'

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    sku_id = db.Column(db.Integer, db.ForeignKey('sku.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    cart = db.relationship('Cart', back_populates='items')
    sku = db.relationship('SKU')

    def __repr__(self):
        return f'<CartItem Cart:{self.cart_id} SKU:{self.sku_id} Qty:{self.quantity}>'

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address_line_1 = db.Column(db.String(255), nullable=False)
    address_line_2 = db.Column(db.String(255))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    is_default = db.Column(db.Boolean, default=False)

    user = db.relationship('User')

class ShippingMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class OrderStatus(enum.Enum):
    PENDING = 'pending'
    PAID = 'paid'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELED = 'canceled'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    shipping_address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User')
    shipping_address = db.relationship('Address')
    items = db.relationship('OrderItem', back_populates='order', cascade="all, delete-orphan")
    payment = db.relationship('Payment', back_populates='order', uselist=False, cascade="all, delete-orphan")

class OrderItemStatus(enum.Enum):
    UNFULFILLED = 'unfulfilled'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELED = 'canceled'

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    sku_id = db.Column(db.Integer, db.ForeignKey('sku.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False) # Price at time of purchase
    fulfillment_status = db.Column(db.Enum(OrderItemStatus), default=OrderItemStatus.UNFULFILLED, nullable=False)

    order = db.relationship('Order', back_populates='items')
    sku = db.relationship('SKU')

class PaymentStatus(enum.Enum):
    PENDING = 'pending'
    SUCCESS = 'success'
    FAILED = 'failed'

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False, unique=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    transaction_id = db.Column(db.String(255)) # From payment gateway
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    order = db.relationship('Order', back_populates='payment')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', back_populates='reviews')
    product = db.relationship('Product', back_populates='reviews')

    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='_user_product_uc'),)

    def __repr__(self):
        return f'<Review {self.id} by User {self.user_id} for Product {self.product_id}>'
