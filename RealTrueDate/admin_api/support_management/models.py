from django.db import models

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return self.question

class AboutUs(models.Model):
    content = models.TextField()

    def __str__(self):
        return "About Us"

    class Meta:
        verbose_name = "About Us"
        verbose_name_plural = "About Us"

class PrivacyPolicy(models.Model):
    content = models.TextField()

    def __str__(self):
        return "Privacy Policy"

    class Meta:
        verbose_name = "Privacy Policy"
        verbose_name_plural = "Privacy Policy"

class ContactUs(models.Model):
    username = models.CharField(max_length=100)  # User's name
    email = models.EmailField()  # User's email
    message = models.TextField()  # Message or inquiry
    reply = models.TextField(blank=True, null=True)  # Reply to the message
    replied = models.BooleanField(default=False)  # Indicates if the message has been replied to

    def __str__(self):
        return f"{self.username} - {self.message[:50]}"