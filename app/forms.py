# Form Related Imports
from wtforms.validators import (
    Length,
    InputRequired,
    ValidationError,
    Regexp,
)  # Validators
from wtforms import StringField, PasswordField, TextAreaField  # Form Fields
from flask_wtf.file import FileField, FileAllowed  # File Upload
from flask_login import current_user  # Current User
from flask_wtf import FlaskForm  # Form
from app.models import User  # Models


# Login form
class LoginForm(FlaskForm):
    """
    Login form
    """

    username = StringField(
        "Username",
        validators=[
            InputRequired(),
            Length(min=3, max=32),
            Regexp("^[a-zA-Z0-9_]+$", message="Username must be alphanumeric."),
        ],
    )  # Username + validators (required, length, regex)

    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=8, max=32)]
    )  # Password + validators (required, length)


# Signup form
class SignupForm(FlaskForm):
    """
    Signup form
    """

    username = StringField(
        "Username",
        validators=[
            InputRequired(),
            Length(
                min=3, max=64, message="Username must be between 3 and 64 characters"
            ),
            Regexp("^[a-zA-Z0-9_]+$", message="Username must be alphanumeric."),
        ],
    )  # Username + validators (required, length, regex)

    password = PasswordField(
        "Password",
        validators=[
            InputRequired(),
            Length(min=8, message="Password must be at least 8 characters long"),
        ],
    )  # Password + validators (required, length)

    def validate_username(self, username):  # Validate username (unique)
        user = User.query.filter_by(username=username.data).first()  # Get user
        if user:  # If user exists
            raise ValidationError(
                "That username is already taken."
            )  # Prompt user to try again with a different username


# Update Profile form
class UpdateProfileForm(FlaskForm):
    """
    Update Profile form
    """

    username = StringField(
        "Username",
        validators=[
            InputRequired(),
            Length(
                min=3, max=64, message="Username must be between 3 and 64 characters"
            ),
            Regexp("^[a-zA-Z0-9_]+$", message="Username must be alphanumeric."),
        ],
    )  # Username + validators (required, length, regex)

    about_user = TextAreaField(
        "About You",
        validators=[
            InputRequired(),
            Length(
                min=3,
                max=1024,
                message="About User must be between 3 and 1024 characters",
            ),
        ],
    )  # About User + validators (required, length)

    picture = FileField(
        "Profile Picture",
        validators=[
            FileAllowed(
                ["jpg", "png", "jpeg", "gif"],
                "Images (jpg, png, jpeg) & GIFs (gif) only!",
            )
        ],
    )  # Picture + validators (file allowed)

    def validate_username(self, username):  # Validate username (unique)
        if username.data != current_user.username:  # If username is different
            user = User.query.filter_by(username=username.data).first()  # Get user
            if user:  # If user exists
                raise ValidationError(
                    "That username is already taken."
                )  # Prompt user to try again with a different username


# Create Clip form
class CreateClipForm(FlaskForm):
    """
    Create Clip form
    """

    title = StringField(
        "Title",
        validators=[
            InputRequired(),
            Length(
                min=3,
                max=64,
                message="Title must be between 3 and 64 characters",
            ),
        ],
    )  # Title + validators (required, length)

    description = TextAreaField(
        "Description",
        validators=[
            InputRequired(),
            Length(
                min=3,
                max=1024,
                message="Description must be between 3 and 1024 characters",
            ),
        ],
    )  # Description + validators (required, length)

    file = FileField(
        "Clip",
        validators=[
            InputRequired(),
            FileAllowed(
                ["mp4", "mov", "avi", "wmv", "flv", "mpg", "mpeg"],
                "Video files (mp4, mov, avi, wmv, flv, mpg, mpeg) only!",
            ),
        ],
    )  # File + validators (required, file allowed)
