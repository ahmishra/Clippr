from datetime import datetime  # DateTime
from slugify import slugify  # Other
from dateutil import tz  # Timezone
from app import app  # App
import pytz  # Timezone

# Slugify - custom filter
@app.template_filter("slugify")
def slug(text):
    return slugify(text)  # Slugify text


@app.template_filter("standardize_date")
def standard_date(datetime_object):
    # Determine difference between now and stamp
    now = datetime.utcnow()
    diff = now - datetime_object

    # Show year in formatting if date is not this year
    if (diff.days / 365) >= 1:
        fmt = "%b %d '%y @ %I:%M%p"
    else:
        fmt = "%b %d @ %I:%M%p"

    users_tz = tz.tzlocal()

    # Give the naive stamp timezone info
    utc_dt = datetime_object.replace(tzinfo=pytz.utc)
    # Convert from utc to local time
    loc_dt = utc_dt.astimezone(users_tz)
    # Apply formatting
    f = loc_dt.strftime(fmt)

    return f  # Return formatted date
