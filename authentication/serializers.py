from rest_framework import serializers
from .models import OTPVerification, User
from django.utils import timezone


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'user_type', 'password']

    def validate(self, data):
        if not data.get('email') and not data.get('phone_number'):
            raise serializers.ValidationError("Either email or phone number is required.")
        if data.get('email') and data.get('phone_number'):
            raise serializers.ValidationError("You can only use one method of registration: email or phone.")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        otp = OTPVerification.objects.create(user=user, otp_code=OTPVerification().generate_otp())
        return user


class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    otp_code = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        phone_number = data.get('phone_number')
        otp_code = data.get('otp_code')

        if not email and not phone_number:
            raise serializers.ValidationError("Email or phone number is required.")
        if email and phone_number:
            raise serializers.ValidationError("Only one method is allowed for verification.")

        try:
            user = User.objects.get(email=email) if email else User.objects.get(phone_number=phone_number)
            otp_entry = user.otp_verification
            if otp_entry.otp_code != otp_code:
                raise serializers.ValidationError("Invalid OTP.")
            if otp_entry.is_expired():
                raise serializers.ValidationError("OTP expired.")
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        return data
