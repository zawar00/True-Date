from django.urls import path, include

urlpatterns = [
     path('auth/', include('api.routes.auth_urls')),          # Include Auth URLs
     path('user/', include('api.routes.user_profile_urls')),  # Include UserProfile URLs
#      path('match', include('api.routes.match_urls')),         # Include Match URLs
#      path('messag', include('api.routes.message_urls')),       # Include Message URLs
]
