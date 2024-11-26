import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from django.conf import settings
import uuid
import mimetypes
import re

# Define size limits (in bytes)
IMAGE_SIZE = int(settings.IMAGE_SIZE_LIMIT) * 1024 * 1024  # Convert MB to bytes
VIDEO_SIZE = int(settings.VIDEO_SIZE_LIMIT) * 1024 * 1024  # Convert MB to bytes

VALID_IMAGE_EXTENSIONS = settings.VALID_IMAGE_EXTENSIONS
VALID_VIDEO_EXTENSIONS = settings.VALID_VIDEO_EXTENSIONS

def get_presigned_url(file_key, expiration=3600):
    """
    Generate a pre-signed URL for accessing an S3 object.

    Args:
        file_key (str): The key (path) of the object in the S3 bucket.
        expiration (int): Time in seconds until the URL expires.

    Returns:
        str: Pre-signed URL for accessing the object.
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

    try:
        # Generate a pre-signed URL
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': file_key
            },
            ExpiresIn=expiration
        )
        return url
    except ClientError as e:
        error_message = e.response.get("Error", {}).get("Message", str(e))
        raise RuntimeError(f"Failed to generate pre-signed URL: {error_message}")

def upload_file_to_s3(file):
    """
    Uploads a file to an AWS S3 bucket with size limits for images and videos.

    Args:
        file: File object to upload.

    Returns:
        dict: Metadata of the uploaded file, including a pre-signed URL.
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

    # Determine the MIME type of the file
    mime_type, _ = mimetypes.guess_type(file.name)
    folder_name = "others"  # Default folder for unknown file types

    if not isinstance(file.size, int):
        raise ValueError("Invalid file size. File size must be an integer.")

    # Check file type and size limits
    if mime_type:
        file_extension = file.name.lower().rsplit('.', 1)[-1]
        if mime_type.startswith("image"):
            folder_name = "images"
            if file_extension not in VALID_IMAGE_EXTENSIONS:
                raise ValueError("Invalid image file format.")
            if file.size > IMAGE_SIZE:
                raise ValueError(f"Image file size exceeds the {settings.IMAGE_SIZE_LIMIT} MB limit.")
        elif mime_type.startswith("video"):
            folder_name = "videos"
            if file_extension not in VALID_VIDEO_EXTENSIONS:
                raise ValueError("Invalid video file format.")
            if file.size > VIDEO_SIZE:
                raise ValueError(f"Video file size exceeds the {settings.VIDEO_SIZE_LIMIT} MB limit.")
        elif mime_type == "application/json":
            folder_name = "results"  # New folder for analysis results
        else:
                raise ValueError("Unsupported file type.")
    else:
        raise ValueError("Could not determine the file type. Please check the file.")

    # Generate a unique filename
    safe_file_name = re.sub(r'[^A-Za-z0-9_.-]', '_', file.name)
    file_name = f"{folder_name}/{uuid.uuid4().hex}_{safe_file_name}"

    try:
        # Upload the file to S3
        s3_client.upload_fileobj(
            file,
            settings.AWS_STORAGE_BUCKET_NAME,
            file_name,
            ExtraArgs={"ACL": "private"}  # Ensure the file is private
        )

        # Generate a pre-signed URL for accessing the uploaded file
        pre_signed_url = get_presigned_url(file_name)

        # Return metadata about the uploaded file
        return {
            "url": pre_signed_url,  # Temporary URL for accessing the file
            "file_name": file.name,
            "folder": folder_name,
            "s3_key": file_name,  # Key used to reference the object in S3
            "mime_type": mime_type,
            "size": file.size
        }

    except NoCredentialsError:
        raise RuntimeError("AWS credentials are missing or invalid.")
    except PartialCredentialsError:
        raise RuntimeError("Incomplete AWS credentials provided.")
    except ClientError as e:
        error_message = e.response.get("Error", {}).get("Message", str(e))
        raise RuntimeError(f"Failed to upload file to S3: {error_message}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")
