from django.urls import path, include

urlpatterns = [
    path('auth/', include('user_api.users.urls')),
    path('profiles/', include('user_api.profiles.urls')),
    path('video/', include('user_api.video_analysis.urls')),
#     path('matching/', include('matching.urls')),
#     path('messaging/', include('messaging.urls')),
]
