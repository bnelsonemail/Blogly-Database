"""Blogly application."""

import logging
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash
# from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
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
        _type_: Show all users in database.
    """
    users = User.query.all()  # Fetch all users from the database
    return render_template('home.html', users=users)


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


@app.route("/", methods=["POST"])
def add_user():
    """Add user and redirect to details."""
    first_name = request.form['first_name'].lower()
    last_name = request.form['last_name'].lower()
    birthdate_str = request.form['birthdate']  # string from form submission
    image_url = request.form['image_url']

    try:
        birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
    except ValueError:
        flash("Invalid date format.  Please use YYY-MM-DD.", 'error')
        return redirect('/')

    user = User(first_name=first_name, last_name=last_name,
                birthdate=birthdate, image_url=image_url)

    try:
        # Add new user to the session and commit the changes

        db.session.add(user)
        db.session.commit()
        flash(f"User {first_name} {last_name} added successfully!", 'success')
        return redirect(f"/{user.id}")
    except IntegrityError:
        # Rollback the session to avoid partial changes
        db.session.rollback()
        flash(f"Error: The name '{first_name}' '{last_name}' is already in "
              f"use. Please choose another one.", 'error')
        return redirect('/error')


@app.route("/<int:user_id>")
def show_user(user_id):
    """Show user info on a single page."""
    # user = {
    #     'id': user_id,
    #     'first_name': 'test_firstname',
    #     'last_name': 'test_lastname',
    #     'birthdate': '1990-01-01',
    #     'image_url': 'null'
    # }
    user = User.query.get_or_404(user_id)
    print(user)  # Debugging: print user details to console
    flash(f"User: {user.first_name} {user.last_name}, ID: {user.id}")
    return render_template("detail.html", user=user)


@app.route("/<int:user_id>/edit")
def edit_user(user_id):
    """Edit user info on a single page."""
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        birthdate_str = request.form['birthdate']
        try:
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.  Please use YYY-MM-DD.', 'error')
            return redirect(f"/user/{user_id}/edit")

        # Use the method to upte the user
        user.update(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            birthdate=birthdate,
            image_url=request.form['image_url']
        )

        try:
            db.session.commit()
            flash('User updated successfully!', 'success')
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred.  Please try again.', 'error')

    print(user)  # Debugging: print user details to console
    flash(f"User: {user.first_name} {user.last_name}, ID: {user.id}")
    return render_template("detail.html", user=user)


if __name__ == '__main__':
    app.run()
