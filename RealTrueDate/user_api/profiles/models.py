from django.db import models
from user_api.users.models import User

# Create your models here.


class Block(models.Model):
    blocker = models.ForeignKey(User, related_name="blocker", on_delete=models.CASCADE)
    blocked = models.ForeignKey(User, related_name="blocked", on_delete=models.CASCADE)
    reason = models.TextField(null=True, blank=True)  # Optional reason for blocking
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')  # Prevent duplicate blocks

    def __str__(self):
        return f"{self.blocker.email} blocked {self.blocked.email} for {self.reason or 'no reason'}"
