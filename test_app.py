"""Test app for application."""

import pytest
from app import app, db  # Import your Flask app and the database instance
from models import User  # Import your User model


def test_home_page(client):
    """Test if the home page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome' in response.data  # Check if 'Welcome' is in the response


def test_add_user(client):
    """Test adding a new user."""
    # Simulate POST request to add a new user
    response = client.post('/', data={
        'first_name': 'TestFirst',
        'last_name': 'TestLast',
        'birthdate': '1990-01-01',
        'image_url': ''
    }, follow_redirects=True)

    # Check if user was added and redirected correctly
    assert response.status_code == 200
    # Check if the user's full name is in the response
    assert b'TestFirst TestLast' in response.data


def test_user_detail(client):
    """Test viewing a user's detail page."""
    # First, add a user to the test database
    user = User(first_name="John", last_name="Doe", birthdate="1990-01-01",
                image_url="")
    db.session.add(user)
    db.session.commit()

    # Now test fetching the user's detail page
    response = client.get(f'/user/{user.id}')
    assert response.status_code == 200
    assert b'John Doe' in response.data  # Check if the correct user is shown
