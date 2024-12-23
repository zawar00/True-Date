from django.urls import path
from .views import VideoUploadView, VideoAnalysisResultView, VideoAnalyzeView

urlpatterns = [
    path('upload/', VideoUploadView.as_view(), name='video-upload'),
    path('<int:video_id>/result/', VideoAnalysisResultView.as_view(), name='video-result'),
    path('analyze/<int:video_id>/', VideoAnalyzeView.as_view(), name='video-analyze'),
]
