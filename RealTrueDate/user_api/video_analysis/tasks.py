from celery import shared_task
from utils.uploadFiles import upload_file_to_s3
from .models import Video, VideoAnalysisResult
from .video_processing import detect_skin_color, detect_eye_color, detect_hair_color, detect_tattoos
import cv2
import json

@shared_task
def analyze_video(video_id=None):
    print("Analyzing video with ID")
    if video_id is None:
        # If no video ID is provided, skip or log an error
        print("No pending video found for analysis.")
        return

#     print(f"Analyzing video with ID: {video_id}")
    try:
        print("Processing video...")
        video = Video.objects.get(id=video_id)
        video.status = 'processing'
        video.save()

        # Download video locally (you can add S3 download logic here)
        local_video_path = "/tmp/video.mp4"  # Example temp path

        cap = cv2.VideoCapture(local_video_path)
        frame_count = 0
        results = {
            "skin_color": None,
            "eye_color": None,
            "hair_color": None,
            "tattoos_detected": False,
        }

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % 30 == 0:  # Process every 30th frame
                if results["skin_color"] is None:
                    results["skin_color"] = detect_skin_color(frame)
                if results["eye_color"] is None:
                    results["eye_color"] = detect_eye_color(frame)
                if not results["tattoos_detected"]:
                    results["tattoos_detected"] = detect_tattoos(frame)

        cap.release()

        # Save results to a JSON file
        result_path = f"/tmp/{video_id}_result.json"
        with open(result_path, 'w') as f:
            json.dump(results, f)

        # Upload result file to S3
        with open(result_path, 'rb') as result_file:
            file_metadata = upload_file_to_s3(result_file)

        VideoAnalysisResult.objects.create(
            video=video,
            result_file_url=file_metadata["url"],
            **results
        )

        video.status = 'completed'
        video.save()

    except Exception as e:
        video.status = 'failed'
        video.save()
        raise e