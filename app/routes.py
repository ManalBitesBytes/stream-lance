from flask import Blueprint, request, jsonify
from .__init__ import db, bcrypt  # Import db and bcrypt instances
from .models import User, UserPreference  # Import your models
from sqlalchemy.exc import IntegrityError  # For handling unique constraint violations

# Define a Blueprint for your API routes
bp = Blueprint('api', __name__, url_prefix='/api')

ALL_CATEGORIES = [
    "AI/ML & Data Science", "Web Development", "Mobile Development",
    "Software Engineering", "Game Development", "Design & Creative",
    "Digital Marketing", "Content & Writing", "System Admin & DevOps",
    "IT & Support", "Business & Consulting", "Engineering & Architecture",
    "Admin & Data Entry", "Other"  # "Other" should generally not be a user preference
]
MAX_CATEGORIES_PER_USER = 3

@bp.route('/register', methods=['POST'])
def register():
    """
    API endpoint for user registration.
    Expects JSON: {"email": "user@example.com", "password": "securepassword"}
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    # Hash the password before storing it
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password_hash=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()  # Commit to save the new user to the database
        return jsonify({"message": "User registered successfully", "user_id": new_user.id}), 201
    except IntegrityError:
        db.session.rollback()  # Rollback in case of an error (e.g., duplicate email)
        return jsonify({"message": "User with this email already exists"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500


@bp.route('/login', methods=['POST'])
def login():
    """
    API endpoint for user login.
    Expects JSON: {"email": "user@example.com", "password": "securepassword"}
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    # Check if user exists and password is correct
    if user and bcrypt.check_password_hash(user.password_hash, password):
        # In a real application, you would generate and return a JWT token here
        # For this project, we'll simply return the user_id for session management in Streamlit
        return jsonify({"message": "Login successful", "user_id": user.id}), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 401


@bp.route('/users/<int:user_id>/preferences', methods=['GET', 'PUT'])
def user_preferences(user_id):
    """
    API endpoint for managing user preferences (categories).
    GET: Retrieve user's current preferences.
    PUT: Overwrite user's preferences with a new list of categories (up to MAX_CATEGORIES_PER_USER).
    Expects JSON for PUT: {"categories": ["Web Development", "AI/ML & Data Science"]}
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    if request.method == 'GET':
        prefs = [p.category_name for p in user.preferences]
        return jsonify({"user_id": user_id, "preferences": prefs}), 200

    elif request.method == 'PUT':
        data = request.get_json()
        new_categories = data.get('categories', [])

        if not isinstance(new_categories, list):
            return jsonify({"message": "Categories must be a list"}), 400

        if len(new_categories) > MAX_CATEGORIES_PER_USER:
            return jsonify({"message": f"You can select up to {MAX_CATEGORIES_PER_USER} categories only."}), 400

        # Validate against known categories
        invalid_categories = [cat for cat in new_categories if cat not in ALL_CATEGORIES or cat == "Other"]
        if invalid_categories:
            return jsonify({"message": f"Invalid categories provided: {', '.join(invalid_categories)}"}), 400

        # Use a set to handle unique categories from input
        unique_new_categories = set(new_categories)

        try:
            # Delete all existing preferences for the user
            UserPreference.query.filter_by(user_id=user_id).delete()
            db.session.commit()  # Commit the deletion

            # Add new preferences
            for cat_name in unique_new_categories:
                new_pref = UserPreference(user_id=user_id, category_name=cat_name)
                db.session.add(new_pref)

            db.session.commit()

            updated_prefs = [p.category_name for p in user.preferences]  # Re-fetch to ensure consistency
            return jsonify({"message": f"Preferences updated successfully.", "preferences": updated_prefs}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"An error occurred while updating preferences: {str(e)}"}), 500

