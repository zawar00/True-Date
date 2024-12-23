from django.urls import path, include

urlpatterns = [
    path('profile_review/', include('admin_api.profile_review.urls')),
    path('support_management/', include('admin_api.support_management.urls')),
    path('transaction_management/', include('admin_api.transaction_management.urls')),
    path('dashboard/', include('admin_api.dashboard.urls')),
]
