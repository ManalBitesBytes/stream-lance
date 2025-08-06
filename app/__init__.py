# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS

import os
import logging

# Initialize the logging configuration for the entire application
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

db = SQLAlchemy()
bcrypt = Bcrypt()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    CORS(app)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")

    db.init_app(app)
    bcrypt.init_app(app)

    # ADD THIS LINE: Make the db instance directly accessible via the app object
    app.db = db

    # Register API blueprint first
    from .routes import bp as api_bp
    app.register_blueprint(api_bp)

    # Then register frontend blueprint
    from .frontend_routes import bp as frontend_bp
    app.register_blueprint(frontend_bp)

    with app.app_context():
        db.create_all()  # Create tables if they don't exist

    return app
