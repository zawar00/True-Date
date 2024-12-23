from django.urls import path
from .views import MatchListView, SwipeViewSet

urlpatterns = [
    path('matches/', MatchListView.as_view(), name='user-matches'),
    path('swipes/', SwipeViewSet.as_view(), name='swipe-action'),
    path('right-swipes/', SwipeViewSet.as_view(), name='right-swipes'),
]
