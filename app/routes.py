from flask import Blueprint, request, jsonify
from .__init__ import db, bcrypt
from .models import User, Gig, UserPreference, SentNotification
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from flask import session
from sqlalchemy import func
import logging

# Configure logging for this blueprint
logger = logging.getLogger(__name__)

# Define a Blueprint for your API routes
bp = Blueprint('api', __name__, url_prefix='/api')

# List of all possible categories (must match your etl/transform/data_transformer.py categories)
ALL_CATEGORIES = [
    "AI/ML & Data Science", "Web Development", "Mobile Development",
    "Software Engineering", "Game Development", "Design & Creative",
    "Digital Marketing", "Content & Writing", "System Admin & DevOps",
    "IT & Support", "Business & Consulting", "Engineering & Architecture",
    "Admin & Data Entry", "Other"
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

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password_hash=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"User registered successfully: {email}")
        return jsonify({"message": "User registered successfully", "user_id": new_user.id}), 201
    except IntegrityError:
        db.session.rollback()
        logger.warning(f"Registration failed: User with email {email} already exists.")
        return jsonify({"message": "User with this email already exists"}), 409
    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred during registration for {email}: {str(e)}", exc_info=True)
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['user_email'] = user.email
        logger.info(f"User logged in successfully: {email}")
        return jsonify({"message": "Login successful", "user_id": user.id, "email": user.email}), 200
    else:
        logger.warning(f"Login failed for {email}: Invalid credentials.")
        return jsonify({"message": "Invalid email or password"}), 401

@bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    logger.info("User logged out successfully")
    return jsonify({"message": "Logged out successfully"}), 200

@bp.route('/current_user', methods=['GET'])
def current_user():
    if 'user_id' in session:
        return jsonify({
            "user_id": session['user_id'],
            "email": session['user_email']
        }), 200
    return jsonify({"message": "No user logged in"}), 401


@bp.route("/users/<int:user_id>/preferences", methods=["PUT"])
def set_user_preferences(user_id):
    """
    API endpoint for setting/updating user preferences (categories).
    Expects JSON: {"categories": ["Web Development", "AI/ML & Data Science"]}
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    if not data or 'categories' not in data:
        return jsonify({"message": "Categories data is required in the request body."}), 400

    categories = data['categories']
    if not isinstance(categories, list) or not categories:
        return jsonify({"message": "Preferences must be a non-empty list of categories."}), 400

    invalid_categories = [cat for cat in categories if cat not in ALL_CATEGORIES or cat == "Other"]
    if invalid_categories:
        return jsonify({
            "message": f"Invalid categories provided: {', '.join(invalid_categories)}. Please choose from valid options."}), 400

    if len(categories) > MAX_CATEGORIES_PER_USER:
        return jsonify({"message": f"You can select a maximum of {MAX_CATEGORIES_PER_USER} categories."}), 400

    try:
        UserPreference.query.filter_by(user_id=user_id).delete()
        db.session.commit()

        for cat_name in categories:
            new_pref = UserPreference(user_id=user_id, category_name=cat_name)
            db.session.add(new_pref)

        db.session.commit()

        updated_prefs = [p.category_name for p in user.preferences]
        logger.info(f"Preferences updated for user {user_id}: {updated_prefs}")
        return jsonify({"message": "Preferences updated successfully.", "preferences": updated_prefs}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while updating preferences for user {user_id}: {str(e)}", exc_info=True)
        return jsonify({"message": f"An error occurred while updating preferences: {str(e)}"}), 500

@bp.route("/users/<int:user_id>/preferences", methods=["GET"])
def get_user_preferences(user_id):
    """
    API endpoint for retrieving user preferences.
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    prefs = [p.category_name for p in user.preferences]
    logger.info(f"Retrieved preferences for user {user_id}: {prefs}")
    return jsonify({"user_id": user_id, "preferences": prefs}), 200

@bp.route("/gigs/recommended/<int:user_id>", methods=["GET"])
def get_recommended_gigs(user_id):
    """
    API endpoint for retrieving gigs recommended to a user based on their preferences
    and published within the last 6 hours.
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    user_preferences = [p.category_name for p in user.preferences]
    if not user_preferences:
        logger.info(f"User {user_id} has no preferences set for recommended gigs.")
        return jsonify({
            "message": "Please set your preferences first to get recommendations.",
            "gigs": []
        }), 200

    time_cutoff = datetime.utcnow() - timedelta(hours=6)

    try:
        recommended_gigs = Gig.query.filter(
            Gig.category.in_(user_preferences),
            Gig.published_at >= time_cutoff
        ).order_by(Gig.published_at.desc()).all()

        gigs_data = []
        if recommended_gigs:
            for gig in recommended_gigs:
                gigs_data.append({
                    "id": gig.id,
                    "title": gig.title,
                    "link": gig.link,
                    "description": gig.description,
                    "category": gig.category,
                    "budget_amount": str(gig.budget_amount) if gig.budget_amount else None,
                    "budget_currency": gig.budget_currency,
                    "skills": gig.skills,
                    "source_platform": gig.source_platform,
                    "published_at": gig.published_at.isoformat() if gig.published_at else None
                })
            logger.info(f"Found {len(gigs_data)} recommended gigs for user {user_id}.")
            return jsonify({"message": "Recommended gigs found", "gigs": gigs_data}), 200
        else:
            logger.info(f"No new gigs matching preferences for user {user_id} in last 6 hours.")
            return jsonify({
                "message": "No new gigs matching your preferences found in the last 6 hours. We will send newer ones to your email!",
                "gigs": []
            }), 200

    except Exception as e:
        logger.error(f"Error fetching recommended gigs for user {user_id}: {str(e)}", exc_info=True)
        return jsonify({"message": "Internal server error"}), 500


@bp.route('/stats', methods=['GET'])
def get_stats():
    try:
        # Count active gigs (published in last 30 days)
        time_cutoff = datetime.utcnow() - timedelta(days=30)
        active_gigs = Gig.query.filter(Gig.published_at >= time_cutoff).count()

        # Calculate average budget (exclude nulls)
        avg_budget = db.session.query(func.avg(Gig.budget_amount)) \
                          .filter(Gig.budget_amount.isnot(None)) \
                          .scalar() or 0

        # Count active freelancers
        freelancers = User.query.count()
        delivered_gigs = SentNotification.query.count()
        stats = {
            "active_gigs": active_gigs,
            "avg_budget": round(float(avg_budget), 2),
            "freelancers": freelancers,
            "delivered_gigs": delivered_gigs
        }

        return jsonify(stats), 200

    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return jsonify({"message": f"Error fetching stats: {str(e)}"}), 500


@bp.route('/trending_categories', methods=['GET'])
def get_trending_categories():
    try:
        # Time windows: last 2 days vs. previous 2 days
        current_window = datetime.utcnow() - timedelta(days=2)
        previous_window = datetime.utcnow() - timedelta(days=4)

        # Fetch gig counts
        current_counts = db.session.query(Gig.category, func.count(Gig.id)) \
            .filter(Gig.published_at >= current_window) \
            .group_by(Gig.category) \
            .all()
        previous_counts = db.session.query(Gig.category, func.count(Gig.id)) \
            .filter(Gig.published_at.between(previous_window, current_window)) \
            .group_by(Gig.category) \
            .all()

        current_dict = dict(current_counts)
        previous_dict = dict(previous_counts)
        trending_data = []
        total_current_gigs = sum(count for _, count in current_counts) or 1

        # Calculate trends (skip "Other" and low-activity categories)
        for category in ALL_CATEGORIES:
            if category == "Other" or current_dict.get(category, 0) < 3:
                continue

            current = current_dict.get(category, 0)
            previous = previous_dict.get(category, 0)
            change_pct = max(0, ((current - previous) / (previous or 1)) * 100)

            trending_data.append({
                "name": category,
                "change": f"+{change_pct:.0f}%",
            })

        # Sort by highest growth rate
        trending_data.sort(key=lambda x: -float(x["change"].rstrip('%')))

        return jsonify(trending_data[:5]), 200

    except Exception as e:
        logger.error(f"Trending categories error: {str(e)}", exc_info=True)
        return jsonify({"message": "Failed to load trends"}), 500