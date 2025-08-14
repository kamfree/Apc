from flask import Flask, render_template
from .extensions import db, login_manager, mail
from .models import User
from .seeds import seed_data_if_needed
from .blueprints.auth import auth_bp
from .blueprints.shop import shop_bp
from .blueprints.cart import cart_bp
from .blueprints.vendor import vendor_bp
from .blueprints.admin import admin_bp
from .blueprints.account import account_bp
from .api.routes import api_bp
from .email import init_email
import os


def create_app():
    app = Flask(__name__, instance_relative_config=False, template_folder="templates", static_folder="static")
    app.config.from_object("config.Config")

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    init_email(app)

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(vendor_bp, url_prefix="/vendor")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(account_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.context_processor
    def inject_globals():
        from .models import Category
        categories = Category.query.order_by(Category.name).all()
        return {"all_categories": categories}

    @app.route("/")
    def index():
        return render_template("index.html")

    # Create DB and seed if needed
    with app.app_context():
        if not os.path.exists(os.path.join(app.root_path, "..", "ecommerce.db")):
            db.create_all()
        else:
            db.create_all()
        seed_data_if_needed()

    return app