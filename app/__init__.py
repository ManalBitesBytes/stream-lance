import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app():
    """
    Creates and configures the Flask application.
    """
    # Create an instance of the Flask class
    app = Flask(__name__)

    # Configure the database and secret key
    # Use os.getenv instead of os.environ.get as it's a common pattern
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    # This is a critical line from your code to prevent deprecation warnings and save resources
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")

    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)

    # Automatically create the database tables if they don't exist
    # This block is from your code and is very useful for development.
    with app.app_context():
        db.create_all()

    # Register the main route for the front end files
    @app.route('/')
    def serve_index():
        """
        Serves the main index.html file.
        This is the entry point for the web application.
        The index.html file will then link to the CSS and JS files automatically.
        """
        return render_template('index.html')

    # Since you have a 'static' folder for your CSS and JS,
    # Flask will automatically serve these files. No need for a separate route.
    # The links in index.html like href="styles.css" will resolve to the static folder.

    # Register the routes blueprint from your other file
    # from .routes import bp as api_bp
    # app.register_blueprint(api_bp)

    return app

# This is what gunicorn will use to run the application
# We'll create the app instance directly from the factory function.
app = create_app()

