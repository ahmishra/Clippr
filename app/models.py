# Database imports
from sqlalchemy import Column, Integer, DateTime, String  # Database
from flask_login import UserMixin  # Database
from flask import url_for  # To generate URLs
from app import db  # Database
import datetime  # DateTime
import json  # To convert to JSON


# Database model for the likes provided by the users to the clips (many-to-many relationship)
class ClipLike(db.Model):
    """
    Clip Likes
    """

    __tablename__ = "clip_like"
    like_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey("user.user_id"))
    clip_id = Column(Integer, db.ForeignKey("clip.clip_id"))


# User Model
class User(UserMixin, db.Model):
    """
    Stores data for website's users
    """

    user_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    username = Column(String(64), unique=True, nullable=False)
    password = Column(String(32))
    picture = Column(String(64), nullable=False, default="default.png")
    about_user = Column(
        String(1024),
        nullable=False,
        default="Apparently, this user has not yet written anything about themselves.",
    )
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    clips = db.relationship("Clip", backref="user", lazy=True)
    comments = db.relationship("Comment", backref="user", lazy=True)

    def get_id(self):
        """
        Required for flask-login
        """
        return self.user_id

    def __repr__(self):
        """
        __repr__: returns a string representation of the object
        """
        return f"<User#{self.user_id}; USERNAME:{self.username};>"

    def __str__(self):
        """
        __str__: returns a string representation of the object
        """
        return f"<User#{self.user_id}; USERNAME:{self.username};>"

    def like_clip(self, clip):
        """
        To like clip
        """
        if not self.has_liked_clip(clip):
            like = ClipLike(user_id=self.user_id, clip_id=clip.clip_id)
            db.session.add(like)

    def unlike_clip(self, clip):
        """
        To unlike clip
        """
        if self.has_liked_clip(clip):
            ClipLike.query.filter_by(
                user_id=self.user_id, clip_id=clip.clip_id
            ).delete()

    def has_liked_clip(self, clip):
        """
        To check if user has liked clip already
        """
        return (
            ClipLike.query.filter(
                ClipLike.user_id == self.user_id, ClipLike.clip_id == clip.clip_id
            ).count()
            > 0
        )

    def to_json(self):
        """
        To convert to JSON
        """
        return json.dumps(
            {
                "user_id": self.user_id,
                "username": self.username,
                "picture": url_for(
                    "static", filename=f"images/profile-pictures/{self.picture}"
                ),
                "about_user": self.about_user,
                "created_date": self.created_date.strftime("%Y-%m-%d %H:%M:%S"),
                "link_to_profile": url_for("profile", username=self.username),
            },
            indent=4,
        )


# Clips Model
class Clip(db.Model):
    """
    Stores all of the clips
    """

    clip_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    user_id = Column(Integer, db.ForeignKey("user.user_id"))
    title = Column(String(64), nullable=False)
    description = Column(db.String(783), nullable=False)
    file = Column(String(64), nullable=False)
    comments = db.relationship("Comment", backref="clip", lazy=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    likes = db.relationship("ClipLike", backref="clip", lazy=True)

    def get_id(self):
        """
        To get clip ID
        """
        return self.clip_id

    def __repr__(self):
        """
        __repr__: returns a string representation of the object
        """
        return f"<Clip#{self.user_id}; CLIP:{self.title};>"

    def __str__(self):
        """
        __str__: returns a string representation of the object
        """
        return f"<Clip#{self.user_id}; CLIP:{self.title};>"


class Comment(db.Model):
    """
    Stores all of the comments for the clips
    """

    comment_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    user_id = Column(Integer, db.ForeignKey("user.user_id"))
    clip_id = Column(Integer, db.ForeignKey("clip.clip_id"))
    comment = Column(db.String(783), nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    def get_id(self):
        """
        To get comment ID
        """
        return self.comment_id

    def __repr__(self):
        """
        __repr__: returns a string representation of the object
        """
        return f"<Comment#{self.comment_id}; CLIP:{self.clip_id};>"

    def __str__(self):
        """
        __str__: returns a string representation of the object
        """
        return f"<Comment#{self.comment_id}; CLIP:{self.clip_id};>"
