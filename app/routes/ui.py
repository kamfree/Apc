from flask import Blueprint, render_template

ui_bp = Blueprint('ui', __name__)

@ui_bp.get('/')
def home_page():
	return render_template('home.html')

@ui_bp.get('/categories')
def categories_page():
	return render_template('categories.html')

@ui_bp.get('/product/<int:product_id>')
def product_page(product_id: int):
	return render_template('product.html', product_id=product_id)

@ui_bp.get('/cart')
def cart_page():
	return render_template('cart.html')

@ui_bp.get('/checkout')
def checkout_page():
	return render_template('checkout.html')

@ui_bp.get('/dashboard')
def dashboard_page():
	return render_template('dashboard.html')