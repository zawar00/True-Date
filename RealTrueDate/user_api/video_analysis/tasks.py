from celery import shared_task
from utils.uploadFiles import upload_file_to_s3, download_video_from_s3
from .models import Video, VideoAnalysisResult
from .video_processing import detect_face_and_features
import json
import os
import numpy as np
import logging
import tempfile
import shutil

# Set up logging
logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=5, default_retry_delay=30)
def analyze_video(self, video_id=None):
    if video_id is None:
        logger.error("No video ID provided for analysis.")
        return

    # Create a temporary directory for file processing
    temp_dir = tempfile.mkdtemp()

    try:
        # Fetch the video object from the database
        video = Video.objects.select_related().get(id=video_id)  # Using select_related for efficiency
        if video is None:
            logger.error(f"Video with ID {video_id} not found.")
            return

        logger.info(f"Started processing video {video_id} with metadata: {json.dumps(video.metadata, default=str)}")
        video.status = 'processing'
        video.save()

        # Temporary file paths
        local_video_path = os.path.join(temp_dir, f"{video_id}_video.mp4")
        result_path = os.path.join(temp_dir, f"{video_id}_result.json")

        # Get the S3 key from the Video model
        s3_key = video.metadata.get("s3_key")
        if not s3_key:
            logger.error(f"No S3 key found for video {video_id}. Cannot download the video.")
            video.status = 'failed'
            video.save()
            return

        # Download the video from S3
        logger.info(f"Downloading video from S3 using key: {s3_key}")
        download_video_from_s3(s3_key, local_video_path)

        # Detect face features from the video
        logger.info(f"Running face and feature detection for video {video_id}")
        skin_color, hair_color, eye_color, tattoos_detected = detect_face_and_features(local_video_path)

        # If no features are detected, mark the video as failed
        if all(feature is None for feature in [skin_color, hair_color, eye_color, tattoos_detected]):
            logger.error(f"No face features detected in video {video_id}")
            video.status = 'failed'
            video.save()
            return

        # Convert features to serializable format
        face_features_serializable = convert_to_serializable({
            "skin_color": skin_color,
            "hair_color": hair_color,
            "eye_color": eye_color,
            "tattoos_detected": tattoos_detected
        })

        logger.info(f"Face features detected: {face_features_serializable}")

        # Save the results to a JSON file
        with open(result_path, 'w') as f:
            json.dump(face_features_serializable, f)
        logger.info(f"Results saved to temporary file: {result_path}")

        # Upload results to S3 (if needed)
        # upload_file_to_s3(result_path, f"results/{video_id}_result.json")

        # Save the analysis result in the database
        VideoAnalysisResult.objects.create(
            video=video,
            skin_color=face_features_serializable.get("skin_color"),
            eye_color=face_features_serializable.get("eye_color"),
            hair_color=face_features_serializable.get("hair_color"),
            tattoos_detected=face_features_serializable.get("tattoos_detected", False)
        )

        # Update the video status to completed
        video.status = 'completed'
        video.save()
        logger.info(f"Video analysis completed successfully for video {video_id}")

    except Video.DoesNotExist:
        logger.error(f"Video with ID {video_id} does not exist.")
    except Exception as e:
        logger.error(f"Error processing video {video_id}: {str(e)}")
        video.status = 'failed'
        video.save()
        self.retry(countdown=10, exc=e)  # Retry task in case of transient errors
    finally:
        # Clean up temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logger.info(f"Temporary files cleaned up for video {video_id}")


def convert_to_serializable(data):
    """Recursively convert numpy types and sets to native Python types."""
    if isinstance(data, dict):
        return {key: convert_to_serializable(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_serializable(item) for item in data]
    elif isinstance(data, set):  # Convert set to list
        return list(data)
    elif isinstance(data, np.int64):  # Handle numpy.int64
        return int(data)  # Convert numpy.int64 to int
    elif isinstance(data, np.float64):  # Handle numpy.float64
        return float(data)  # Convert numpy.float64 to float
    return data  # Return the data if no conversion is necessary
