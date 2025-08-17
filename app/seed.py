from app import create_app, db
from app.models import User, VendorProfile, Category, Product, ProductVariant, Inventory

app = create_app()
with app.app_context():
	db.create_all()
	# Users
	admin = User.query.filter_by(email='admin@example.com').first()
	if not admin:
		admin = User(email='admin@example.com', role='admin')
		admin.set_password('Admin123!')
		db.session.add(admin)
	
	alice = User.query.filter_by(email='alice@example.com').first()
	if not alice:
		alice = User(email='alice@example.com', role='vendor', first_name='Alice', last_name='Doe')
		alice.set_password('Secret123!')
		db.session.add(alice)
		db.session.flush()
		vp = VendorProfile(user_id=alice.id, company_name='Alice Co', bio='We sell stuff', is_approved=True)
		db.session.add(vp)
	
	bob = User.query.filter_by(email='bob@example.com').first()
	if not bob:
		bob = User(email='bob@example.com', role='customer', first_name='Bob', last_name='Smith')
		bob.set_password('Password123!')
		db.session.add(bob)
	
	# Category
	cat = Category.query.filter_by(slug='electronics').first()
	if not cat:
		cat = Category(name='Electronics', slug='electronics', description='Gadgets')
		db.session.add(cat)
		db.session.flush()
	
	# Product
	prod = Product.query.filter_by(slug='seed-phone').first()
	if not prod:
		prod = Product(vendor_id=alice.id, category_id=cat.id, name='Seed Phone', slug='seed-phone', description='A demo smartphone', price=399.99, currency='USD')
		db.session.add(prod)
		db.session.flush()
		variant = ProductVariant(product_id=prod.id, sku='SEED-PHONE-1', name='Default', attributes=None, price_override=None)
		db.session.add(variant)
		db.session.flush()
		inv = Inventory(variant_id=variant.id, quantity=50)
		db.session.add(inv)
	
	db.session.commit()
	print('Seeded: admin, alice (vendor), bob (customer), electronics category, seed phone product')