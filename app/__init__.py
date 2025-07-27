from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app():
    """
    Creates and configures the Flask application.
    """
    app = Flask(__name__)

    # Configure database URI from environment variables
    # Fallback values are provided but ensure your .env is loaded correctly
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/mydb")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Suppress SQLAlchemy track modifications warning

    # Configure Flask secret key from environment variables (essential for session security)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY",
                                         "super_secret_dev_key")  # IMPORTANT: Change for production!

    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)

    # Import and register blueprints or routes here
    # This registers the API routes defined in app/routes.py
    from . import routes
    app.register_blueprint(routes.bp)

    # Create database tables within the application context
    # This will create tables defined in models.py if they don't already exist
    with app.app_context():
        db.create_all()

    return app