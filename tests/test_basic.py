import os
import json
import pytest

from app import create_app, db

@pytest.fixture()
def app():
	app = create_app()
	app.config.update(TESTING=True)
	with app.app_context():
		db.drop_all()
		db.create_all()
		yield app

@pytest.fixture()
def client(app):
	return app.test_client()


def register_and_login(client):
	client.post('/api/auth/register', json={'email':'u@example.com','password':'Pass123!'})
	r = client.post('/api/auth/login', json={'email':'u@example.com','password':'Pass123!'})
	return r.json['access_token']


def test_health(client):
	r = client.get('/health')
	assert r.status_code == 200


def test_cart_and_checkout_flow(app, client):
	# seed vendor and product
	with app.app_context():
		from app.models import User, VendorProfile, Category, Product, ProductVariant, Inventory
		v = User(email='v@example.com', role='vendor'); v.set_password('Vendor123!'); db.session.add(v); db.session.flush();
		db.session.add(VendorProfile(user_id=v.id, company_name='V Co', is_approved=True))
		c = Category(name='C1', slug='c1'); db.session.add(c); db.session.flush()
		p = Product(vendor_id=v.id, category_id=c.id, name='P1', slug='p1', price=10.0, currency='USD'); db.session.add(p); db.session.flush()
		var = ProductVariant(product_id=p.id, sku='SKU1'); db.session.add(var); db.session.flush();
		db.session.add(Inventory(variant_id=var.id, quantity=5));
		db.session.commit()

	# customer
	token = register_and_login(client)

	# add to cart
	r = client.post('/api/cart/add', json={'variant_id':1,'quantity':2}, headers={'Authorization': f'Bearer {token}'})
	assert r.status_code == 201

	# checkout
	payload = {'shipping_address':{'full_name':'T','line1':'1','city':'X','postal_code':'1','country':'US'}, 'billing_address':{'full_name':'T','line1':'1','city':'X','postal_code':'1','country':'US'}}
	r = client.post('/api/orders/checkout', json=payload, headers={'Authorization': f'Bearer {token}'})
	assert r.status_code == 201

	# stock reduced
	with app.app_context():
		from app.models import Inventory
		inv = Inventory.query.first()
		assert inv.quantity == 3