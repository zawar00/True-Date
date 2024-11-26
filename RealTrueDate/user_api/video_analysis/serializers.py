from rest_framework import serializers
from .models import Video, VideoAnalysisResult

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'user', 'file_url', 'uploaded_at', 'status', 'metadata']

class VideoAnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoAnalysisResult
        fields = ['id', 'video', 'skin_color', 'eye_color', 'hair_color', 'tattoos_detected', 'result_file_url', 'created_at']
