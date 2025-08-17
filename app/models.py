from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class User(db.Model):
	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255), unique=True, nullable=False, index=True)
	password_hash = db.Column(db.String(255), nullable=False)
	role = db.Column(db.String(50), nullable=False, default='customer')  # customer, vendor, admin
	first_name = db.Column(db.String(120))
	last_name = db.Column(db.String(120))
	is_active = db.Column(db.Boolean, default=True, nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	vendor_profile = db.relationship('VendorProfile', uselist=False, back_populates='user', cascade='all, delete-orphan')

	def set_password(self, password: str) -> None:
		self.password_hash = generate_password_hash(password)

	def check_password(self, password: str) -> bool:
		return check_password_hash(self.password_hash, password)

	def to_dict(self):
		return {
			'id': self.id,
			'email': self.email,
			'role': self.role,
			'first_name': self.first_name,
			'last_name': self.last_name,
			'is_active': self.is_active,
			'created_at': self.created_at.isoformat() if self.created_at else None,
			'updated_at': self.updated_at.isoformat() if self.updated_at else None,
		}


class VendorProfile(db.Model):
	__tablename__ = 'vendor_profiles'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
	company_name = db.Column(db.String(255))
	bio = db.Column(db.Text)
	is_approved = db.Column(db.Boolean, default=False, nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	user = db.relationship('User', back_populates='vendor_profile')


class Category(db.Model):
	__tablename__ = 'categories'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255), nullable=False, unique=True)
	slug = db.Column(db.String(255), nullable=False, unique=True, index=True)
	description = db.Column(db.Text)
	parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	parent = db.relationship('Category', remote_side=[id], backref=db.backref('children', lazy='dynamic'))

	def to_dict(self):
		return {
			'id': self.id,
			'name': self.name,
			'slug': self.slug,
			'description': self.description,
			'parent_id': self.parent_id,
		}


class Product(db.Model):
	__tablename__ = 'products'

	id = db.Column(db.Integer, primary_key=True)
	vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
	category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
	name = db.Column(db.String(255), nullable=False)
	slug = db.Column(db.String(255), nullable=False, unique=True, index=True)
	description = db.Column(db.Text)
	price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
	currency = db.Column(db.String(3), nullable=False, default='USD')
	is_active = db.Column(db.Boolean, default=True, nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	vendor = db.relationship('User', backref=db.backref('products', lazy='dynamic'))
	category = db.relationship('Category', backref=db.backref('products', lazy='dynamic'))
	images = db.relationship('ProductImage', back_populates='product', cascade='all, delete-orphan')
	variants = db.relationship('ProductVariant', back_populates='product', cascade='all, delete-orphan')

	def to_dict(self, include_images=True, include_variants=True):
		data = {
			'id': self.id,
			'vendor_id': self.vendor_id,
			'category_id': self.category_id,
			'name': self.name,
			'slug': self.slug,
			'description': self.description,
			'price': float(self.price or 0),
			'currency': self.currency,
			'is_active': self.is_active,
		}
		if include_images:
			data['images'] = [img.to_dict() for img in self.images]
		if include_variants:
			data['variants'] = [v.to_dict(include_inventory=True) for v in self.variants]
		return data


class ProductImage(db.Model):
	__tablename__ = 'product_images'

	id = db.Column(db.Integer, primary_key=True)
	product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
	url = db.Column(db.String(1024), nullable=False)
	is_primary = db.Column(db.Boolean, default=False, nullable=False)
	sort_order = db.Column(db.Integer, default=0, nullable=False)

	product = db.relationship('Product', back_populates='images')

	def to_dict(self):
		return {
			'id': self.id,
			'product_id': self.product_id,
			'url': self.url,
			'is_primary': self.is_primary,
			'sort_order': self.sort_order,
		}


class ProductVariant(db.Model):
	__tablename__ = 'product_variants'

	id = db.Column(db.Integer, primary_key=True)
	product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
	sku = db.Column(db.String(120), unique=True, nullable=False)
	name = db.Column(db.String(255))
	attributes = db.Column(db.JSON)  # e.g., {"color": "red", "size": "M"}
	price_override = db.Column(db.Numeric(10, 2))
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	product = db.relationship('Product', back_populates='variants')
	inventory = db.relationship('Inventory', uselist=False, back_populates='variant', cascade='all, delete-orphan')

	def effective_price(self):
		return float(self.price_override if self.price_override is not None else (self.product.price or 0))

	def to_dict(self, include_inventory=False):
		data = {
			'id': self.id,
			'product_id': self.product_id,
			'sku': self.sku,
			'name': self.name,
			'attributes': self.attributes or {},
			'price': self.effective_price(),
		}
		if include_inventory:
			data['inventory'] = self.inventory.to_dict() if self.inventory else None
		return data


class Inventory(db.Model):
	__tablename__ = 'inventory'

	id = db.Column(db.Integer, primary_key=True)
	variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=False, unique=True)
	quantity = db.Column(db.Integer, default=0, nullable=False)
	low_stock_threshold = db.Column(db.Integer, default=5, nullable=False)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	variant = db.relationship('ProductVariant', back_populates='inventory')

	def to_dict(self):
		return {
			'id': self.id,
			'variant_id': self.variant_id,
			'quantity': int(self.quantity or 0),
			'low_stock_threshold': int(self.low_stock_threshold or 0),
		}


class Cart(db.Model):
	__tablename__ = 'carts'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
	session_id = db.Column(db.String(128), index=True)
	status = db.Column(db.String(50), default='active', nullable=False)  # active, ordered, abandoned
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	user = db.relationship('User', backref=db.backref('carts', lazy='dynamic'))
	items = db.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')

	def to_dict(self):
		return {
			'id': self.id,
			'user_id': self.user_id,
			'session_id': self.session_id,
			'status': self.status,
			'items': [i.to_dict() for i in self.items],
			'totals': self.compute_totals(),
		}

	def compute_totals(self):
		subtotal = 0.0
		for item in self.items:
			subtotal += item.total_price()
		return {
			'subtotal': round(float(subtotal), 2),
			'currency': 'USD',
		}

	def merge_from(self, other: 'Cart'):
		if not other or other.id == self.id:
			return
		# Merge items by variant
		variant_id_to_item = {i.variant_id: i for i in self.items}
		for o_item in other.items:
			if o_item.variant_id in variant_id_to_item:
				variant_id_to_item[o_item.variant_id].quantity += o_item.quantity
			else:
				self.items.append(CartItem(variant_id=o_item.variant_id, quantity=o_item.quantity, unit_price=o_item.unit_price))
		# Clear other cart
		other.items.clear()
		other.status = 'abandoned'


class CartItem(db.Model):
	__tablename__ = 'cart_items'

	id = db.Column(db.Integer, primary_key=True)
	cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False, index=True)
	variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=False)
	quantity = db.Column(db.Integer, default=1, nullable=False)
	unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	cart = db.relationship('Cart', back_populates='items')
	variant = db.relationship('ProductVariant')

	def total_price(self) -> float:
		return round(float(self.unit_price or 0) * int(self.quantity or 0), 2)

	def to_dict(self):
		return {
			'id': self.id,
			'cart_id': self.cart_id,
			'variant_id': self.variant_id,
			'quantity': self.quantity,
			'unit_price': float(self.unit_price or 0),
			'total_price': self.total_price(),
			'variant': self.variant.to_dict(include_inventory=True) if self.variant else None,
		}


class Address(db.Model):
	__tablename__ = 'addresses'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
	full_name = db.Column(db.String(255))
	line1 = db.Column(db.String(255), nullable=False)
	line2 = db.Column(db.String(255))
	city = db.Column(db.String(120), nullable=False)
	state = db.Column(db.String(120))
	postal_code = db.Column(db.String(30), nullable=False)
	country = db.Column(db.String(2), nullable=False, default='US')
	is_default_shipping = db.Column(db.Boolean, default=False, nullable=False)
	is_default_billing = db.Column(db.Boolean, default=False, nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	user = db.relationship('User', backref=db.backref('addresses', lazy='dynamic'))

	def to_dict(self):
		return {
			'id': self.id,
			'user_id': self.user_id,
			'full_name': self.full_name,
			'line1': self.line1,
			'line2': self.line2,
			'city': self.city,
			'state': self.state,
			'postal_code': self.postal_code,
			'country': self.country,
		}


class ShippingMethod(db.Model):
	__tablename__ = 'shipping_methods'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), nullable=False)
	price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
	estimated_days = db.Column(db.Integer, default=5, nullable=False)
	is_active = db.Column(db.Boolean, default=True, nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	def to_dict(self):
		return {
			'id': self.id,
			'name': self.name,
			'price': float(self.price or 0),
			'estimated_days': self.estimated_days,
			'is_active': self.is_active,
		}


class Order(db.Model):
	__tablename__ = 'orders'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
	status = db.Column(db.String(50), default='pending', nullable=False)  # pending, paid, processing, shipped, delivered, cancelled
	payment_status = db.Column(db.String(50), default='unpaid', nullable=False)  # unpaid, paid, refunded
	total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
	currency = db.Column(db.String(3), nullable=False, default='USD')
	shipping_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'))
	billing_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'))
	shipping_method_id = db.Column(db.Integer, db.ForeignKey('shipping_methods.id'))
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	user = db.relationship('User')
	shipping_address = db.relationship('Address', foreign_keys=[shipping_address_id])
	billing_address = db.relationship('Address', foreign_keys=[billing_address_id])
	shipping_method = db.relationship('ShippingMethod')
	items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
	payments = db.relationship('Payment', back_populates='order', cascade='all, delete-orphan')

	def to_dict(self, include_items=True):
		data = {
			'id': self.id,
			'user_id': self.user_id,
			'status': self.status,
			'payment_status': self.payment_status,
			'total_amount': float(self.total_amount or 0),
			'currency': self.currency,
			'shipping_method': self.shipping_method.to_dict() if self.shipping_method else None,
		}
		if include_items:
			data['items'] = [i.to_dict() for i in self.items]
		return data


class OrderItem(db.Model):
	__tablename__ = 'order_items'

	id = db.Column(db.Integer, primary_key=True)
	order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
	product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
	variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=False)
	vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
	quantity = db.Column(db.Integer, nullable=False)
	unit_price = db.Column(db.Numeric(10, 2), nullable=False)
	total_price = db.Column(db.Numeric(10, 2), nullable=False)
	fulfillment_status = db.Column(db.String(50), default='pending', nullable=False)  # pending, fulfilled, shipped
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	order = db.relationship('Order', back_populates='items')
	product = db.relationship('Product')
	variant = db.relationship('ProductVariant')
	vendor = db.relationship('User')

	def to_dict(self):
		return {
			'id': self.id,
			'order_id': self.order_id,
			'product_id': self.product_id,
			'variant_id': self.variant_id,
			'vendor_id': self.vendor_id,
			'quantity': int(self.quantity or 0),
			'unit_price': float(self.unit_price or 0),
			'total_price': float(self.total_price or 0),
			'fulfillment_status': self.fulfillment_status,
		}


class Payment(db.Model):
	__tablename__ = 'payments'

	id = db.Column(db.Integer, primary_key=True)
	order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
	provider = db.Column(db.String(50), nullable=False, default='mock')
	amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
	currency = db.Column(db.String(3), nullable=False, default='USD')
	status = db.Column(db.String(50), nullable=False, default='pending')  # pending, paid, failed, refunded
	transaction_id = db.Column(db.String(120))
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

	order = db.relationship('Order', back_populates='payments')

	def to_dict(self):
		return {
			'id': self.id,
			'order_id': self.order_id,
			'provider': self.provider,
			'amount': float(self.amount or 0),
			'currency': self.currency,
			'status': self.status,
			'transaction_id': self.transaction_id,
		}


class Review(db.Model):
	__tablename__ = 'reviews'

	id = db.Column(db.Integer, primary_key=True)
	product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
	rating = db.Column(db.Integer, nullable=False)
	title = db.Column(db.String(255))
	body = db.Column(db.Text)
	is_approved = db.Column(db.Boolean, default=False, nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	user = db.relationship('User')
	product = db.relationship('Product')

	def to_dict(self):
		return {
			'id': self.id,
			'product_id': self.product_id,
			'user_id': self.user_id,
			'rating': int(self.rating or 0),
			'title': self.title,
			'body': self.body,
			'is_approved': self.is_approved,
			'created_at': self.created_at.isoformat() if self.created_at else None,
		}