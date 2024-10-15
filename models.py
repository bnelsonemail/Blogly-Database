"""Models for Blogly."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import DetachedInstanceError

db = SQLAlchemy()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User Class."""

    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    first_name = db.Column(db.String(20),
                           nullable=False)
    last_name = db.Column(db.String(20),
                          nullable=False)
    birthdate = db.Column(db.Date,
                          nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        """Show information about user."""

        u = self
        try:
            return (f"<User id={u.id} first_name={u.first_name} "
                    f"last_name={u.last_name} birthdate={u.birthdate} "
                    f"image_url={u.image_url}>")
        except DetachedInstanceError:
            return "<Detached User Error>"

    def update(self, first_name=None, last_name=None, birthdate=None,
               image_url=None):
        """Update the user's information."""
        s = self
        if first_name:
            s.first_name = first_name.lower()
        if last_name:
            s.last_name = last_name.lower()
        if birthdate:
            s.birthdate = birthdate
        if image_url:
            s.image_url = image_url

    def delete(self):
        """Delete the user from the database."""
        db.session.delete(self)
        db.session.commit()
