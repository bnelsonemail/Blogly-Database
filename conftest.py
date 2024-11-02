"""Testing Applicatition with Pytest."""

import sys
import os
import pytest
from app import app, db
from models import User

# Add the project root directory to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def client():
    """Fixture to set up a test client and test database."""
    app.config.from_object('config.TestingConfig')  # Load test config
    with app.test_client() as test_client:
        with app.app_context():
            db.create_all()  # Create tables in the test database
            yield test_client  # Provide the test client to tests
            db.drop_all()  # Clean up (drop all tables) after each test
