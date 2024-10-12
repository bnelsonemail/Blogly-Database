"""Blogly application."""

import logging
import os
# from flask import Flask, render_template, redirect, flash, session
# from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from dotenv import load_dotenv
# from models import db, connect_db

from config import DevelopmentConfig, ProductionConfig, TestingConfig


# Load environment variables from .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

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

# Disable SQLAlchemy logging in production
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Enable Debug Toolbar for development
debug = DebugToolbarExtension(app)

# Initialize the database with the app
# connect_db(app)


# Define a route
@app.route('/')
def index():
    """Welcome page.

    Returns:
        _type_: Welcome greeting to page.
    """
    return "Welcome to the Blogly application!"


# Custom CLI command to create database tables
@app.cli.command("create-db")
def create_db():
    """Creates the database tables."""
    db.create_all()
    print("Database tables created!")


if __name__ == '__main__':
    app.run()
