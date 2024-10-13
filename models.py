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
    birthdate = db.Column(db.String(10),
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
