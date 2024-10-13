from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db

# Define the 'User' model, representing the users table in the database.
class User(UserMixin, db.Model):
    # Primary key: Unique identifier for each user.
    id = db.Column(db.Integer, primary_key=True)

    # User's email, must be unique and cannot be null.
    email = db.Column(db.String(100), unique=True, nullable=False)

    # First name of the user, cannot be null.
    first_name = db.Column(db.String(50), nullable=False)

    # Last name of the user, cannot be null.
    last_name = db.Column(db.String(50), nullable=False)

    # Hash of the user's password.
    password_hash = db.Column(db.String(200))

    # Boolean field indicating if the user has admin privileges (defaults to False).
    is_admin = db.Column(db.Boolean, default=False)

    # Method to set the user's password, which is hashed before storing it.
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Method to check if the provided password matches the stored hashed password.
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


