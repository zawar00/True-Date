from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Video, VideoAnalysisResult
from .serializers import VideoSerializer, VideoAnalysisResultSerializer
from .tasks import analyze_video
from utils.uploadFiles import upload_file_to_s3

class VideoUploadView(APIView):
    def post(self, request):
        user = request.user  # Assuming authentication is in place
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            file_metadata = upload_file_to_s3(file)

            video = Video.objects.create(
                user=user,
                file_url=file_metadata["url"],
                metadata={
                    "file_name": file_metadata["file_name"],
                    "s3_key": file_metadata["s3_key"],
                    "mime_type": file_metadata["mime_type"],
                    "size": file_metadata["size"],
                },
            )
            print("Video uploaded successfully")
            print("Scheduling video analysis task...", video.id)
            analyze_video.delay(video.id)
            print("Video analysis task scheduled")

            return Response({"message": "Video uploaded successfully", "video": VideoSerializer(video).data}, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except RuntimeError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VideoAnalysisResultView(APIView):
    def get(self, request, video_id):
        try:
            video = Video.objects.get(id=video_id, user=request.user)
            print(video.status)

            if video.status == 'pending':
                return Response({"message": "Video is still being pending"}, status=status.HTTP_202_ACCEPTED)
            elif video.status == 'completed':
               result = video.analysis_result
               return Response(VideoAnalysisResultSerializer(result).data, status=status.HTTP_200_OK)
            elif video.status == 'processing':
                return Response({"message": "Video is still being processed"}, status=status.HTTP_202_ACCEPTED)
            elif video.status == 'failed':
                return Response({"error": "Video processing failed"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Unknown video status"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)
