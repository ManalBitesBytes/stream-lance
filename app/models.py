from datetime import datetime
from .__init__ import db # Import the SQLAlchemy instance from __init__.py

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    registered_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.utcnow)


    preferences = db.relationship('UserPreference', backref='user', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"

# Define the UserPreference model, mapping to the 'user_preferences' table
class UserPreference(db.Model):
    __tablename__ = 'user_preferences' # Explicitly link to the existing 'user_preferences' table
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_name = db.Column(db.String(100), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'category_name', name='_user_category_uc'),)

    def __repr__(self):
        return f"<UserPreference User:{self.user_id} Category:{self.category_name}>"

class Gig(db.Model):
    __tablename__ = 'gigs' # Link to the existing 'gigs' table
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512), nullable=False)
    link = db.Column(db.Text, unique=True, nullable=False)
    description = db.Column(db.Text)
    published_at = db.Column(db.TIMESTAMP(timezone=True))
    category = db.Column(db.String(100))
    budget_amount = db.Column(db.Numeric(10, 2))
    budget_currency = db.Column(db.String(10))
    skills = db.Column(db.ARRAY(db.Text)) # PostgreSQL array type
    source_platform = db.Column(db.String(50))
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f"<Gig {self.title[:50]}...>"

class SentNotification(db.Model):
    __tablename__ = 'sent_notifications' # Link to the existing 'sent_notifications' table
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    gig_id = db.Column(db.Integer, db.ForeignKey('gigs.id', ondelete='CASCADE'), nullable=False)
    sent_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'gig_id', name='_user_gig_notification_uc'),)

    def __repr__(self):
        return f"<SentNotification User:{self.user_id} Gig:{self.gig_id}>"

