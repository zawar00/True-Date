from django.urls import path
from .views import VideoUploadView, VideoAnalysisResultView

urlpatterns = [
    path('upload/', VideoUploadView.as_view(), name='video-upload'),
    path('<int:video_id>/result/', VideoAnalysisResultView.as_view(), name='video-result'),
]
