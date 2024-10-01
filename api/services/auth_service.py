from api.models.user_profile import UserOTP
import random
from django.utils import timezone
from datetime import timedelta

def generate_otp(user):
    otp_code = str(random.randint(100000, 999999))
    otp_expiry = timezone.now() + timedelta(minutes=10)
    UserOTP.objects.create(user=user, otp_code=otp_code, expires_at=otp_expiry)
    # Here, you would send the OTP via email/SMS
    print(f"Generated OTP for {user.email}: {otp_code}")
