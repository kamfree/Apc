from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from config import get_config

# Extensions

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_class=None):
    app = Flask(__name__)

    if config_class is None:
        config_class = get_config()

    app.config.from_object(config_class)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Enable CORS (allow credentials and any origin as configured)
    CORS(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}}, supports_credentials=True)

    # Register blueprints (will be created in later steps)
    from .routes import register_blueprints
    register_blueprints(app)

    # Simple health endpoint
    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app