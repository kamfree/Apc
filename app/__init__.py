from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from app import models

    # Blueprints will be registered here later
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from app.routes.vendor import vendor_bp
    app.register_blueprint(vendor_bp, url_prefix='/api/vendor')

    from app.routes.products import products_bp
    app.register_blueprint(products_bp, url_prefix='/api/products')

    from app.routes.cart import cart_bp
    app.register_blueprint(cart_bp, url_prefix='/api/cart')

    from app.routes.orders import orders_bp
    app.register_blueprint(orders_bp, url_prefix='/api/orders')

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    from app.routes.reviews import reviews_bp
    app.register_blueprint(reviews_bp, url_prefix='/api') # Prefixed in the route definitions

    from app.routes.reports import reports_bp
    app.register_blueprint(reports_bp, url_prefix='/api/reports')

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    return app
