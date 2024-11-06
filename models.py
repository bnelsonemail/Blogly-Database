"""Models for Blogly."""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
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

    @property
    def full_name(self):
        """Return full name of user."""
        return f"{self.first_name.capitalize()} {self.last_name.capitalize()}"

    def create_blog_post(self, title, content):
        """Create a new blog post associated with this user."""
        post = BlogPost(user_id=self.id, title=title, content=content)
        db.session.add(post)
        db.session.commit()
        return post


class BlogPost(db.Model):
    """BlogPost Class."""

    __tablename__ = "blog_posts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )

    def __repr__(self):
        """Show information about blog post."""
        return (f"<BlogPost id={self.id} title={self.title}"
                "created_at={self.created_at}>")


class Tag(db.Model):
    """Tag Class."""

    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Relationship to access posts for a tag
    posts = relationship("BlogPost", secondary="post_tags",
                         back_populates="tags")

    def __repr__(self):
        """Show information about tag."""
        return f"<Tag id={self.id} name={self.name}>"


class PostTag(db.Model):
    """Association table for BlogPost and Tag."""

    __tablename__ = "post_tags"

    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"),
                        primary_key=True, nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"), primary_key=True,
                       nullable=False)

    def __repr__(self):
        """Show information about PostTag association."""
        return f"<PostTag post_id={self.post_id} tag_id={self.tag_id}>"
