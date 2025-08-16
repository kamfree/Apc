from flask import render_template, Blueprint

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/login')
def login():
    return render_template('login.html')

@main_bp.route('/register')
def register():
    return render_template('register.html')

@main_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    return render_template('product_detail.html', product_id=product_id)

@main_bp.route('/cart')
def cart():
    return render_template('cart.html')

@main_bp.route('/checkout')
def checkout():
    # This route should be protected by a login requirement in a real app,
    # which would be handled by client-side JS checking for a token.
    return render_template('checkout.html')

@main_bp.route('/dashboard')
def dashboard():
    # Placeholder for vendor/admin/customer dashboards
    return render_template('dashboard.html')
