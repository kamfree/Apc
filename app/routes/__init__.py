from flask import Blueprint


def register_blueprints(app):
	# Register blueprints as they are implemented
	from .auth import auth_bp
	from .vendor import vendor_bp
	from .products import products_bp
	from .cart import cart_bp
	from .orders import orders_bp
	from .reviews import reviews_bp
	from .reports import reports_bp
	from .ui import ui_bp
	app.register_blueprint(auth_bp, url_prefix='/api/auth')
	app.register_blueprint(vendor_bp, url_prefix='/api/vendor')
	app.register_blueprint(products_bp, url_prefix='/api/products')
	app.register_blueprint(cart_bp, url_prefix='/api/cart')
	app.register_blueprint(orders_bp, url_prefix='/api/orders')
	app.register_blueprint(reviews_bp, url_prefix='/api/reviews')
	app.register_blueprint(reports_bp, url_prefix='/api/reports')
	app.register_blueprint(ui_bp)