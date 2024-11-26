from django.db import models
from user_api.users.models import User  # Import User model

class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="uploaded_videos")
    file_url = models.URLField(max_length=1000)  # URL of the video file in AWS S3
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, 
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending',
    )
    metadata = models.JSONField(default=dict, blank=True)  # Optional metadata from upload (e.g., file size, format)

class VideoAnalysisResult(models.Model):
    video = models.OneToOneField(Video, on_delete=models.CASCADE, related_name="analysis_result")
    skin_color = models.CharField(max_length=50, null=True, blank=True)
    eye_color = models.CharField(max_length=50, null=True, blank=True)
    hair_color = models.CharField(max_length=50, null=True, blank=True)
    tattoos_detected = models.BooleanField(default=False)
    result_file_url = models.URLField(null=True, blank=True)  # URL to the JSON file in AWS S3
    created_at = models.DateTimeField(auto_now_add=True)
