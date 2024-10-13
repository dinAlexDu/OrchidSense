from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

# Initialize SQLAlchemy instance for managing database operations.
# This will be used to interact with the database, define models,
# and execute queries.
db = SQLAlchemy()

# Initialize Flask-Mail instance for managing email operations.
# This will be used to send emails from the Flask application.
mail = Mail()
