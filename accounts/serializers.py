from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from academics.models import Student
from .models import Profile


class UserSummarySerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "role")

    def get_role(self, obj):
        if obj.is_staff or obj.is_superuser:
            return Profile.Role.ADMIN
        profile = getattr(obj, "profile", None)
        return getattr(profile, "role", None)


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8, validators=[validate_password])
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    registration_number = serializers.CharField(max_length=40)
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate_registration_number(self, value):
        if Student.objects.filter(registration_number__iexact=value).exists():
            raise serializers.ValidationError("This registration number is already in use.")
        return value.upper()

    @transaction.atomic
    def create(self, validated_data):
        registration_number = validated_data.pop("registration_number")
        phone = validated_data.pop("phone", "")
        user = User.objects.create_user(**validated_data)
        user.profile.role = Profile.Role.STUDENT
        user.profile.save(update_fields=["role", "updated_at"])
        Student.objects.create(
            user=user,
            registration_number=registration_number,
            phone=phone,
        )
        return user

    def to_representation(self, instance):
        return MeSerializer(instance).data


class MeSerializer(UserSummarySerializer):
    student_id = serializers.SerializerMethodField()
    registration_number = serializers.SerializerMethodField()

    class Meta(UserSummarySerializer.Meta):
        fields = UserSummarySerializer.Meta.fields + ("student_id", "registration_number")

    def get_student_id(self, obj):
        student = getattr(obj, "student_profile", None)
        return getattr(student, "id", None)

    def get_registration_number(self, obj):
        student = getattr(obj, "student_profile", None)
        return getattr(student, "registration_number", None)
