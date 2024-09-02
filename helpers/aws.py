import boto3
from dotenv import load_dotenv
import os
import logging

# Get the logger instance from app.py
logger = logging.getLogger("my_app_logger")  # Use the same name as in app.py


def list_s3_items():
    s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION"))
    # Specify your bucket name
    bucket_name = "scrippsresearchngscore-spun"

    # Fetch the list of objects in the specified bucket
    response = s3.list_objects_v2(Bucket=bucket_name)

    # Extract the list of objects from the response
    objects = response.get("Contents", [])

    # Create a list of object keys (file names)
    object_keys = [obj["Key"] for obj in objects]

    # Return the list of object keys as a JSON response
    return object_keys
