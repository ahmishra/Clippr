# Imports
from flask_login import LoginManager  # Auth
from flask_sqlalchemy import SQLAlchemy  # Database
from flask import Flask  # App
from flask_socketio import SocketIO  # Socket IO for quick-chat feature
import eventlet  # Eventlet for async

eventlet.monkey_patch()  # Eventlet for async

# Initialize the app
app = Flask(
    __name__,
)

# App configuraton
app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# SocketIO initialization
socketio = SocketIO(app, async_mode="eventlet")

# Database setup
db = SQLAlchemy(app)

# Login stuff
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "login"

# Loading user model, when all else is done
from app.models import User

# User loader for login manager
@login_manager.user_loader
def load_user(user_id):
    """
    Required for login manager to work.
    """
    return User.query.get(int(user_id))  # Return user object


# Other imports, to avoid circular imports
from app import routes  # Routes
from util import filters  # Filters
