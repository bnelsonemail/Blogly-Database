"""Blogly application."""

import logging
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash
# from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from models import db, connect_db, User, BlogPost, Tag


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
        return redirect(f"/user/{user.id}")
    except IntegrityError:
        # Rollback the session to avoid partial changes
        db.session.rollback()
        flash(f"Error: The name '{first_name}' '{last_name}' is already in "
              f"use. Please choose another one.", 'error')
        return redirect('/error')


@app.route("/user/<int:user_id>")
def show_user(user_id):
    """Show user info on a single page, including their posts."""
    user = User.query.get_or_404(user_id)
    posts = (BlogPost.query
             .filter_by(user_id=user.id)
             .all())  # Fetch posts for the user
    print(user)  # Debugging: print user details to console
    print(posts)  # Debugging: print post details to console
    return render_template("detail.html", user=user, posts=posts)


@app.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    """Edit user info on a single page."""
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        # Get form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        image_url = request.form['image_url']
        birthdate_str = request.form['birthdate']

        # Convert birthdate string to date object
        try:
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return redirect(f'/user/{user_id}/edit')

        # Use the update method in the User model to update attributes
        user.update(
            first_name=first_name,
            last_name=last_name,
            birthdate=birthdate,
            image_url=image_url
        )

        # Commit the changes to the database
        try:
            db.session.commit()
            flash('User updated successfully!', 'success')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'error')
            return redirect(f'/user/{user_id}/edit')

        return redirect(f'/user/{user.id}')

    # Render the edit form with the current user data (GET request)
    return render_template('edit_user.html', user=user)


@app.route('/user/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete the user."""
    user = User.query.get_or_404(user_id)  # Fetch the user from the database

    try:
        user.delete()  # Call the delete method in the User model
        flash(f"User {user.first_name} {user.last_name} deleted successfully!",
              "success")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"An error occurred: {e}", "error")

    return redirect('/')  # redirect to home after deleting the user


@app.route('/users/<int:user_id>/posts/new', methods=['GET', 'POST'])
def new_post(user_id):
    """Show form to create a new post for a user or handle form submission."""
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()  # Fetch all tags to populate the dropdown

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        # Get selected tags from the form
        selected_tag_ids = request.form.getlist('tags')

        if not title or not content:
            flash("Title and content are required.", "error")
            return redirect(request.url)

        try:
            # Create a new post
            post = BlogPost(user_id=user.id, title=title, content=content)
            db.session.add(post)

            # Associate tags with the new post
            if selected_tag_ids:
                tags_to_add = (Tag.query.filter(Tag.id.in_(selected_tag_ids))
                               .all())
                # Assuming BlogPost has a many-to-many relationship with Tag
                post.tags.extend(tags_to_add)

            db.session.commit()

            flash('Post created successfully!', 'success')
            return redirect(f'/user/{user.id}')
        except IntegrityError as e:
            db.session.rollback()
            print(f"Integrity Error: {e}")
            flash("A database integrity error occurred. Check your data"
                  "constraints.", "error")
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Database Error: {e}")
            flash("An error occurred while saving the post. Please try again.",
                  "error")

        return redirect(request.url)

    # Render the template with the user and available tags
    return render_template('new_post.html', user=user, tags=tags)


@app.route('/posts/<int:post_id>')
def show_post(post_id):
    """Show a specific post with its tags."""
    post = BlogPost.query.get_or_404(post_id)

    # The post object should include related tags through the relationship
    return render_template('post_detail.html', post=post)


@app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    """Show form to edit a post or handle edit form submission."""
    post = BlogPost.query.get_or_404(post_id)
    tags = Tag.query.all()  # Fetch all available tags for the dropdown

    if request.method == 'POST':
        # Get title, content, and selected tags from the form
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        selected_tag_ids = request.form.getlist('tags')

        # Update the tags associated with the post
        post.tags = Tag.query.filter(Tag.id.in_(selected_tag_ids)).all()

        try:
            db.session.commit()
            flash('Post updated successfully!', 'success')
            return redirect(f'/posts/{post.id}')
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Database Error: {e}")
            flash("An error occurred while saving the post. Please try again.",
                  "error")
            return redirect(request.url)

    return render_template('edit_post.html', post=post, tags=tags)


@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """Delete a specific post, including its tag associations."""
    post = BlogPost.query.get_or_404(post_id)

    try:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database Error: {e}")
        flash("An error occurred while deleting the post. Please try again.",
              "error")

    return redirect(f'/user/{post.user_id}')


@app.route('/tags/new', methods=['GET', 'POST'])
def new_tag():
    """Show form to create a new tag or handle form submission."""
    # Replace with logic to get the correct user, if applicable
    user = User.query.get(1)

    if request.method == 'POST':
        tag_name = request.form.get('name').strip()

        if not tag_name:
            flash("Tag name is required.", "error")
            return redirect(request.url)

        existing_tag = Tag.query.filter_by(name=tag_name).first()
        if existing_tag:
            flash("Tag with this name already exists.", "error")
            return redirect(request.url)

        try:
            new_tag = Tag(name=tag_name)
            db.session.add(new_tag)
            db.session.commit()
            flash('Tag created successfully!', 'success')
            return redirect('/tags')
        except SQLAlchemyError:
            db.session.rollback()
            flash("An error occurred while creating the tag. "
                  "Please try again.", "error")
            return redirect(request.url)

    return render_template('new_tag.html', user=user)


if __name__ == '__main__':
    app.run()
