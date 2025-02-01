from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from twilio.rest import Client
from .models import OTPVerification
from django.utils import timezone
from django.conf import settings
import random

from .serializers import RegisterSerializer, OTPVerificationSerializer
from .models import User


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Send OTP
            otp_entry = user.otp_verification
            otp_code = otp_entry.otp_code

            if user.email:
                send_mail(
                    subject="Verify Your Email",
                    message=f"Your OTP code is {otp_code}. It will expire in 5 minutes.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email]
                )
            else:
                twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                twilio_client.messages.create(
                    body=f"Your OTP is {otp_code}",
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=user.phone_number
                )

            return Response({"message": "OTP sent successfully!"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerificationView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = request.data.get('email')
            phone_number = request.data.get('phone_number')
            otp_code = request.data.get('otp_code')

            user = User.objects.get(email=email) if email else User.objects.get(phone_number=phone_number)
            otp_entry = user.otp_verification

            if otp_entry.otp_code != otp_code:
                return Response({"message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
            if otp_entry.is_expired():
                return Response({"message": "OTP expired."}, status=status.HTTP_400_BAD_REQUEST)

            user.is_active = True
            user.save()

            # Delete OTP after verification
            otp_entry.delete()

            return Response({"message": "Account verified successfully!"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
