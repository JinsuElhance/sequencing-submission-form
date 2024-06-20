import logging
import pandas as pd
import os
from flask import (
    redirect,
    Blueprint,
    render_template,
    request,
    url_for,
    jsonify,
)
from flask_login import current_user, login_required
from models.bucket import Bucket
from helpers.metadata_check import check_metadata

# Get the logger instance from app.py
logger = logging.getLogger("my_app_logger")  # Use the same name as in app.py

metadata_bp = Blueprint("metadata", __name__)


# Custom admin_required decorator
def admin_required(view_func):
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            # Redirect unauthenticated users to the login page
            return redirect(
                url_for("user.login")
            )  # Adjust 'login' to your actual login route
        elif not current_user.admin:
            # Redirect non-admin users to some unauthorized page
            return redirect(url_for("user.only_admins"))
        return view_func(*args, **kwargs)

    return decorated_view


# Custom approved_required decorator
def approved_required(view_func):
    def decorated_approved_view(*args, **kwargs):
        if not current_user.is_authenticated:
            # Redirect unauthenticated users to the login page
            return redirect(
                url_for("user.login")
            )  # Adjust 'login' to your actual login route
        elif not current_user.approved:
            # Redirect non-approved users to some unauthorized page
            return redirect(url_for("user.only_approved"))
        return view_func(*args, **kwargs)

    return decorated_approved_view


@metadata_bp.route("/metadata_form", endpoint="metadata_form")
@login_required
@approved_required
def metadata_form():
    my_buckets = {}
    map_key = os.environ.get("GOOGLE_MAP_API_KEY")
    for my_bucket in current_user.buckets:
        my_buckets[my_bucket] = Bucket.get(my_bucket)
    return render_template(
        "metadata_form.html", my_buckets=my_buckets, map_key=map_key
    )


@metadata_bp.route(
    "/upload_metadata_file", methods=["POST"], endpoint="upload_metadata_file"
)
@login_required
@approved_required
def upload_metadata_file():
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # Read uploaded file and get its column names
    filename = file.filename
    file_extension = os.path.splitext(filename)[1].lower()

    if file_extension == ".csv":
        df = pd.read_csv(file)
    elif file_extension in [".xls", ".xlsx"]:
        df = pd.read_excel(file, engine="openpyxl")
    else:
        return jsonify({"error": "Unsupported file type"}), 400

    # Check metadata using the helper function
    result = check_metadata(df)

    # Return the result as JSON
    return jsonify(result)
