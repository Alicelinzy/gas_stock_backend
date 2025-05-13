from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'profile_image', 'is_verified', 'role']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']


class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.CharField(required=False, default='customer')
    phone_number = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'phone_number']

    def create(self, validated_data):
        # Extract role before creating user (since it's not a User model field)
        role = validated_data.pop('role', 'customer')
        password = validated_data.pop('password')
        phone_number = validated_data.pop('phone_number', None)
    
        
        # Create user (this will trigger the signal to create a profile)
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()  # Signal creates profile here
        
        # Update the profile's role
        user.profile.role = role
        user.profile.save()
        
        return user

def to_representation(self, instance):
        return UserSerializer(instance).data


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        return {"user": user}


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
