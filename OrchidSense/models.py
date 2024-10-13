from extensions import db, mail
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# User model for the 'users' table in the database.
# This model stores user information such as email, password, names, profile image, and admin status.
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    # Columns of the 'users' table.
    id = db.Column(db.Integer, primary_key=True)  # Primary key, unique identifier for each user.
    email = db.Column(db.String(100), unique=True, nullable=False)  # User's email, must be unique and not null.
    password_hash = db.Column(db.String(200))  # Hashed password, not stored in plain text.
    first_name = db.Column(db.String(100))  # User's first name.
    last_name = db.Column(db.String(100))  # User's last name.
    profile_image = db.Column(db.String(100), default='profile-1.png')  # Profile image with a default value.
    is_admin = db.Column(db.Boolean, default=False)  # Boolean flag to check if the user is an admin.

    # Method to set the user's password by hashing it using Werkzeug's 'generate_password_hash'.
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Method to check the user's password by comparing the stored hash with the given password.
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Orchid model for the 'orquideas' table in the database.
# This model stores information about orchids, such as ideal temperature, humidity, and light conditions.
class Orquidea(db.Model):
    __tablename__ = 'orquideas'

    # Columns of the 'orquideas' table.
    id = db.Column(db.Integer, primary_key=True)  # Primary key, unique identifier for each orchid.
    nome = db.Column(db.String(100), nullable=False)  # Orchid's name, cannot be null.
    temperatura_ideal = db.Column(db.String(50))  # Ideal temperature for the orchid.
    humidade_ideal = db.Column(db.String(50))  # Ideal humidity for the orchid.
    luz_ideal = db.Column(db.String(100))  # Ideal light condition for the orchid.
    descricao = db.Column(db.Text)  # Description of the orchid.
    imagem = db.Column(db.String(255))  # URL or path to the orchid's image.

    # Representation method to display orchid's name when printing the object.
    def __repr__(self):
        return f'<Orquidea {self.nome}>'



# UserConfig model for the 'user_configs' table in the database.
# This model stores the user-specific configurations for monitoring orchid conditions (temperature, humidity, light).
class UserConfig(db.Model):
    __tablename__ = 'user_configs'

    # Columns of the 'user_configs' table.
    id = db.Column(db.Integer, primary_key=True)  # Primary key, unique identifier for each config.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to the 'users' table.
    user = db.relationship('User', backref=db.backref('configs', lazy=True))  # Relationship with the 'User' model.
    orquidea_id = db.Column(db.Integer, db.ForeignKey('orquideas.id'), nullable=False)  # Foreign key to 'orquideas' table.
    temp_min = db.Column(db.Float)  # Minimum temperature configuration for monitoring.
    temp_max = db.Column(db.Float)  # Maximum temperature configuration for monitoring.
    humidade_min = db.Column(db.Float)  # Minimum humidity configuration for monitoring.
    humidade_max = db.Column(db.Float)  # Maximum humidity configuration for monitoring.
    lux_min = db.Column(db.Integer)  # Minimum light level (lux) configuration for monitoring.
    lux_max = db.Column(db.Integer)  # Maximum light level (lux) configuration for monitoring.


