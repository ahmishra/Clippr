from app.forms import (
    LoginForm,
    SignupForm,
    UpdateProfileForm,
    CreateClipForm,
)  # Form Related Imports
from flask import (
    redirect,
    url_for,
    flash,
    request,
    abort,
)  # Redirects + Flashes + Abort
from util.helpers import (
    save_picture,
    save_video,
    delete_video,
    delete_picture,
)  # Helpers
from werkzeug.security import check_password_hash, generate_password_hash  # Auth
from flask_login import login_user, login_required, current_user  # Auth
from app.models import User, Clip, Comment, ClipLike  # Models
from app import app, db, socketio  # App, Database & SocketIO
from flask_login.utils import logout_user  # Logout
from flask import render_template  # Rendering

###############################################################################

# Home page
@app.route("/")
def home():
    """
    Home page
    """

    return render_template("home.html", title="Clippr. - Home")


###############################################################################

###############################################################################

# Delete Account
@app.route("/account/delete", methods=["GET", "POST"])
@login_required
def delete_account():
    """
    Delete Account
    """

    user = User.query.filter_by(user_id=current_user.user_id).first()  # Get User

    # Delete all user clips
    user_clips = Clip.query.filter_by(user_id=user.user_id).all()
    for clip in user_clips:
        delete_video(clip.file)
        db.session.delete(clip)
        db.session.commit()

    # Delete all user comments
    user_comments = Comment.query.filter_by(user_id=user.user_id).all()
    for comment in user_comments:
        db.session.delete(comment)

    # Delete all user likes
    user_likes = ClipLike.query.filter_by(user_id=user.user_id).all()
    for like in user_likes:
        db.session.delete(like)

    # Delete user profile picture
    if user.picture != "default.png":
        delete_picture(user.picture)

    # Delete user
    db.session.delete(user)
    db.session.commit()

    # Redirect to Home
    return redirect(url_for("home"))


# Update profile
@app.route("/update-profile", methods=["GET", "POST"])
@login_required
def update_profile():
    """
    Update profile page
    """

    form = UpdateProfileForm()  # Update profile form
    if form.validate_on_submit():  # If form is submitted and validated
        if form.picture.data:  # If picture is uploaded
            picture = save_picture(form.picture.data)  # Save picture
            current_user.picture = picture  # Update picture

        current_user.username = form.username.data  # Update username
        current_user.about_user = form.about_user.data  # Update username

        db.session.commit()  # Commit changes
        flash("Your profile was updated!", "info")

        return redirect(
            url_for("profile", username=current_user.username)
        )  # Redirect to profile, due to post-get-redirect pattern, to avoid "Are you sure you want to resubmit?"

    elif request.method == "GET":  # If form is not submitted, but GET request
        form.username.data = (
            current_user.username
        )  # Set username to current user's username

        form.about_user.data = (
            current_user.about_user
        )  # Set about_user to current user's about_user

    return render_template(
        "update-profile.html", title="Clippr. - Update Profile", form=form
    )


# Profile (LOGIN REQUIRED)
@app.route("/profile/<username>")
def profile(username):
    """
    Profile (LOGIN REQUIRED)
    """

    user = User.query.filter_by(
        username=username
    ).first()  # Get user according to username passed in

    if user:  # If user exists
        picture = url_for(
            "static", filename=f"images/profile-pictures/{user.picture}"
        )  # Get picture

        return render_template(
            "profile.html", title="Clippr. - Profile", user=user, picture=picture
        )

    else:
        return render_template("profile.html", title="Clippr. - Profile")


###############################################################################

###############################################################################

# Create Clip (LOGIN REQUIRED + GET + POST + CRUD: Create)
@app.route("/create-clip", methods=["GET", "POST"])
@login_required
def create_clip():
    """
    Create Clip
    """

    form = CreateClipForm()  # Create form

    if form.validate_on_submit():  # Validate form
        new_clip = Clip(
            title=form.title.data,
            description=form.description.data,
            file=save_video(form.file.data),
            user_id=current_user.user_id,
        )  # Create new clip
        db.session.add(new_clip)  # Add clip to database
        db.session.commit()  # Commit changes to database

        # Post a default comment to the clip
        new_clip_comment = Comment(
            comment="Hey! Hope so you enjoyed this clip!",
            user_id=new_clip.user_id,
            clip_id=new_clip.clip_id,
        )
        db.session.add(new_clip_comment)  # Add comment to database
        db.session.commit()  # Commit changes to database

        flash("Your clip has been created!", "info")

        return redirect(
            url_for("view_clips")
        )  # Redirect to view clips page after creation of clip

    return render_template("create-clip.html", title="Clippr. - Create Clip", form=form)


# Clip Detail (LOGIN REQUIRED + GET + POST + CRUD: Retrieve)
@app.route("/clip/<string:title>/<int:clip_id>", methods=["GET", "POST"])
@login_required
def clip_detail(title, clip_id):
    _ = title  # Unused (just for URL "decoration")
    """
    Clip Detail
    """

    clip = Clip.query.get(clip_id)  # Get clip

    comments = (
        Comment.query.filter_by(clip_id=clip_id)
        .order_by(Comment.created_date.desc())
        .all()
    )

    return render_template(
        "clip-detail.html",
        title=f"Clippr. - {clip.title}",
        clip=clip,
        user=current_user,
        comments=comments,
    )


# Delete Clip (LOGIN REQUIRED + CRUD: Delete)
@app.route("/delete/clip/<int:clip_id>")
@login_required
def delete_clip(clip_id):
    """
    Delete Clip
    """

    clip = Clip.query.get_or_404(clip_id)  # Get clip else 404
    if (
        clip.user_id != current_user.user_id
    ):  # Abort if user is not the owner of the clip
        abort(403)

    # Delete clip comments
    clip_comments = Comment.query.filter_by(clip_id=clip_id).all()
    clip_likes = ClipLike.query.filter_by(clip_id=clip_id).all()

    for comment in clip_comments:
        db.session.delete(comment)

    for like in clip_likes:
        db.session.delete(like)

    delete_video(clip.file)  # Delete video
    db.session.delete(clip)  # Delete clip
    db.session.commit()  # Commit

    flash("Clip Deleted", "info")  # Flash
    return redirect(url_for("view_clips"))  # Redirect


# View Clips (View all clips)
@app.route("/clips")
def view_clips():
    """
    View all clips
    """

    clips = Clip.query.order_by(Clip.created_date.desc()).all()

    return render_template("view-clips.html", title="Clippr. - Clips", clips=clips)


# Like clip (LOGIN REQUIRED)
@app.route("/like/clip/<int:clip_id>/<action>")
@login_required
def like_action(clip_id, action):
    clip = Clip.query.filter_by(
        clip_id=clip_id
    ).first_or_404()  # Get clip, or get a 404

    if action == "like":  # If like
        current_user.like_clip(clip)  # Like clip
        db.session.commit()  # Commit

    if action == "unlike":  # If unlike
        current_user.unlike_clip(clip)  # Unlike clip
        db.session.commit()  # Commit

    return {"status": "OK", "likes": len(clip.likes)}


###############################################################################

###############################################################################

# Submit Comment (LOGIN REQUIRED + POST)
@app.route("/comment/<int:clip_id>", methods=["POST"])
@login_required
def submit_comment(clip_id):
    """
    Submit Comment
    """

    if request.form["comment"].strip():  # If comment is not empty
        comment = Comment(
            comment=request.form["comment"],
            user_id=current_user.user_id,
            clip_id=clip_id,
        )  # Create comment

    db.session.add(comment)  # Add comment
    db.session.commit()  # Commit

    return {
        "result": "success",
        "comment": comment.comment,
        "user": comment.user.username,
        "user_picture": comment.user.picture,
        "date": comment.created_date,
    }  # Return result


###############################################################################


@app.route("/quick-chat")
@login_required
def quick_chat():
    return render_template("quick-chat.html", title="Clippr. - Quick Chat")


@socketio.on("msg")
def event_handler(json):
    socketio.emit("msg_response", json, callback=None)


connected_clients = []


@socketio.on("connect")
def add_to_connected():
    global connected_clients
    connected_clients.append(current_user.to_json())
    socketio.emit(
        "users",
        {"clients": connected_clients, "total": len(connected_clients), "joined": True},
        broadcast=True,
    )


@socketio.on("disconnect")
def remove_from_connected():
    global connected_clients
    connected_clients.remove(current_user.to_json())
    socketio.emit(
        "users",
        {"clients": connected_clients, "total": len(connected_clients)},
        broadcast=True,
    )


###############################################################################

# Logout (LOGIN REQUIRED + AUTH)
@app.route("/logout")
@login_required
def logout():
    """
    Logout (LOGIN REQUIRED)
    """

    logout_user()  # Logout
    flash("Logged out.", "warning")
    return redirect(url_for("home"))


# LOGIN (GET + POST + AUTH)
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    LOGIN
    """

    # If user is already logged in - redirect to home page
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()  # Loading up the form
    if form.validate_on_submit():  # If form is submitted and validated
        user = User.query.filter_by(username=form.username.data).first()  # Get user
        if user:  # If user exists
            if check_password_hash(
                user.password, form.password.data
            ):  # If password is correct
                login_user(user, remember=True)  # Login user
                flash(f"Welcome, {user.username}!", "info")
                return redirect(url_for("view_clips"))  # Redirect to view clips

        flash("Invalid username or password.", "danger")

    return render_template("login.html", title="Clippr. - Login", form=form)


# SIGNUP (GET + POST + AUTH)
@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    SIGNUP
    """

    # If user is already logged in - redirect to home page
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = SignupForm()  # Loading up the form
    if form.validate_on_submit():  # If form is submitted and validated
        password = generate_password_hash(
            form.password.data, method="sha256"
        )  # Hash password obtained from the form
        username = form.username.data  # Get username from the form

        new_user = User(username=username, password=password)  # Create new user
        db.session.add(new_user)  # Add user to the database
        db.session.commit()  # Commit the changes to the database

        if (
            not current_user.is_authenticated
        ):  # If user didn't got automatically logged in
            flash(f"Hey, {new_user.username}! Login now.", "info")
            return redirect(url_for("login"))

    return render_template("signup.html", title="Clippr. - Signup", form=form)


###############################################################################
