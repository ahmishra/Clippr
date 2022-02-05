from secrets import token_hex  # Hashing
from PIL import Image  # Image Resizing
from app import app  # App
import os  # File System


# Picture uploader
def save_picture(form_picture):
    random_hex = token_hex(8)  # Generate random hex
    _, f_ext = os.path.splitext(form_picture.filename)  # Get file extension
    picture_fn = random_hex + f_ext  # Create filename
    picture_path = os.path.join(
        app.root_path, "static/images/profile-pictures", picture_fn
    )  # Create picture path

    if f_ext != ".gif":  # Resize image if image is not a GIF
        output_size = (512, 512)  # Set output size
        i = Image.open(form_picture)  # Open image
        i.thumbnail(output_size)  # Resize image
        i.save(picture_path)  # Save image
    else:  # If image is a GIF, save it as is
        form_picture.save(picture_path)  # Save picture

    return picture_fn  # Return filename


# Video uploader
def save_video(form_video):
    random_hex = token_hex(8)  # Generate random hex
    _, f_ext = os.path.splitext(form_video.filename)  # Get file extension
    video_fn = random_hex + f_ext  # Create filename
    video_path = os.path.join(
        app.root_path, "static/videos", video_fn
    )  # Create video path

    form_video.save(video_path)  # Save video

    return video_fn  # Return filename


# Video deleter
def delete_video(video_fn):
    video_path = os.path.join(
        app.root_path, "static/videos", video_fn
    )  # Create video path

    os.remove(video_path)  # Remove video


# Picture deleter
def delete_picture(picture_fn):
    picture_path = os.path.join(
        app.root_path, "static/images/profile-pictures", picture_fn
    )  # Create picture path

    os.remove(picture_path)  # Remove picture
