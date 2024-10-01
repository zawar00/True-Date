from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="TrueDate API",
        default_version='v1',
        description="API documentation for the TrueDate application",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/', include('api.app.urls')),
]

