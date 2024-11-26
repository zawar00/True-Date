
from user_api.video_analysis.models import Video  # Adjust this import based on the location of your Video model

def get_next_pending_video():
    """Fetch the next pending video to be analyzed."""
    return Video.objects.filter(status='pending').first()
