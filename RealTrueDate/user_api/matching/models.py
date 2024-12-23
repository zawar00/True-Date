from django.db import models
from user_api.users.models import User

class Swipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swipes')  # The user performing the swipe
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swiped_by')  # The user being swiped on
    direction = models.CharField(max_length=5, choices=[('left', 'Left'), ('right', 'Right')])  # Direction of the swipe
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp of the swipe action

    class Meta:
        unique_together = ('user', 'target_user')  # Ensure one swipe per user-target user pair

    def __str__(self):
        return f"{self.user} swiped {self.direction} on {self.target_user}"