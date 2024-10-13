"""Blogly application."""

import logging
import os
from flask import Flask, render_template  # redirect, flash, session
# from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from models import db, connect_db, User


from config import DevelopmentConfig, ProductionConfig, TestingConfig


# Load environment variables from .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

# Load the SECRET_KEY and other configuration variables from .env file
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Choose the configuration class based on FLASK_ENV from the .env file
env = os.getenv('FLASK_ENV')

if env == 'development':
    app.config.from_object(DevelopmentConfig)
elif env == 'production':
    app.config.from_object(ProductionConfig)
elif env == 'testing':
    app.config.from_object(TestingConfig)
else:
    # Default to development if FLASK_ENV is missing
    app.config.from_object(DevelopmentConfig)

# Check if SECRET_KEY is loaded (debugging purpose)
if not app.config.get('SECRET_KEY'):
    raise RuntimeError("SECRET_KEY not found in Flask app config!")

# Check for db connection
print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])

# Disable SQLAlchemy logging in production
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Enable Debug Toolbar for development
debug = DebugToolbarExtension(app)

# Initialize the database with the app
connect_db(app)
# db.create_all()  # Create the tables in the database


# Define a route
@app.route('/')
def home():
    """Welcome page.

    Returns:
        _type_: Welcome greeting to page.
    """
    return render_template('home.html')


# Custom CLI command to create database tables
@app.cli.command("create-db")
def create_db():
    """Creates the database tables."""
    db.create_all()
    print("Database tables created!")


@app.route('/test-db')
def test_db():
    """Test database connection."""

    try:
        # Simple query to check the connection
        User.query.all()
        return "Database connection successful!"
    except SQLAlchemyError as e:
        return f"Error: {str(e)}"


if __name__ == '__main__':
    app.run()
