from django.urls import path
from file_upload.views import FileUploadAPIView

urlpatterns = [
    path('upload/', FileUploadAPIView.as_view(), name='file-upload'),
]
