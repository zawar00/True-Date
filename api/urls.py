from django.urls import path, include

urlpatterns = [
     path('auth/', include('app.routes.auth_urls')),
     path('profile/', include('app.routes.user_profile_urls')),
]
