from django.urls import path, include


urlpatterns = [
    path("api/v1/user/", include("user_api.urls")),     # Routes for user functionalities
    path("api/v1/admin/", include("admin_api.urls")),   # Routes for admin functionalities
    path("api/v1/files/", include("file_upload.urls")),   # Routes for file upload functionalities
]