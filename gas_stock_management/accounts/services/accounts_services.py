from accounts.repository.accounts_repository import AccountRepository
from accounts.serializers import (
    UserSerializer,
    ProfileSerializer,
    RegisterSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
)
from gas_stock_management.response import RepositoryResponse, APIResponse
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import re
from rest_framework_simplejwt.tokens import RefreshToken


class AccountService:

    @staticmethod
    def register_user(data: dict):
        # Validate phone number format (example for Rwandan phone numbers)
        phone_number = data.get('phone_number', '')
        if phone_number and not re.match(r'^\+2507\d{8}$', phone_number):
            return {
                "success": False,
                "message": "Invalid phone number format",
                "data": {},
                "status_code": status.HTTP_400_BAD_REQUEST
            }

        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            repo_response = AccountRepository.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                phone_number=serializer.validated_data.get('phone_number'),
                role=serializer.validated_data.get('role', 'customer')
            )
            return {
                "success": repo_response.success,
                "message": repo_response.message,
                "data": repo_response.data,
                "status_code": repo_response.status_code
            }
        return {
            "success": False,
            "message": "Invalid input",
            "data": serializer.errors,
            "status_code": status.HTTP_400_BAD_REQUEST
        }

    @staticmethod
    def login_user(data: dict):
        serializer = LoginSerializer(data=data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                refresh = RefreshToken.for_user(user)
                return {
                    "success": True,
                    "message": "Login successful",
                    "data": {
                        "user": UserSerializer(user).data,
                        "tokens": {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        }
                    },
                    "status_code": status.HTTP_200_OK
                }
            return {
                "success": False,
                "message": "Invalid username or password",
                "data": {},
                "status_code": status.HTTP_401_UNAUTHORIZED
            }
        return {
            "success": False,
            "message": "Invalid input",
            "data": serializer.errors,
            "status_code": status.HTTP_400_BAD_REQUEST
        }

    @staticmethod
    def get_user_profile(user_id: int):
        repo_response = AccountRepository.get_user_by_id(user_id)
        
        if repo_response.success:
            # Serialize the user and profile
            user_data = UserSerializer(repo_response.data['user']).data
            profile_data = ProfileSerializer(repo_response.data['profile']).data

            return {
                "success": True,
                "message": "User profile retrieved successfully",
                "data": {
                    "user": user_data,
                    "profile": profile_data
                },
                "status_code": status.HTTP_200_OK
            }
        
        return {
            "success": False,
            "message": "User not found",
            "data": {},
            "status_code": status.HTTP_404_NOT_FOUND
        }

    @staticmethod
    def update_profile(user_id: int, data: dict):
        repo_response = AccountRepository.update_profile(
            user_id=user_id,
            phone_number=data.get("phone_number"),
            address=data.get("address"),
            role=data.get("role"),
            profile_image=data.get("profile_image")
        )
        if repo_response.success:
            profile_data = ProfileSerializer(repo_response.data['profile']).data
            return {
                "success": True,
                "message": "Profile updated successfully",
                "data": profile_data,
                "status_code": status.HTTP_200_OK
            }
        
        return {
            "success": False,
            "message": repo_response.message ,
            "data": {},
            "status_code": repo_response.status_code
        }

    @staticmethod
    def delete_user(user_id: int):
        repo_response = AccountRepository.delete_user_by_id(user_id)
        return {
            "success": repo_response.success,
            "message": repo_response.message or (
                "User deleted successfully" if repo_response.success else "Failed to delete user"
            ),
            "data": repo_response.data,
            "status_code": repo_response.status_code
        }

    @staticmethod
    def get_users_by_role(role: str):
        repo_response = AccountRepository.get_users_by_role(role)
        
        if not repo_response.success:
            return {
                "success": False,
                "message": repo_response.message,
                "data": {},
                "status_code": repo_response.status_code
            }
        
        # The repository returns {"user": user_obj, "profile": profile_obj} for each user
        serialized_users = []
        for user_data in repo_response.data['users']:
            serialized_users.append({
                'user': UserSerializer(user_data['user']).data,
                'profile': ProfileSerializer(user_data['profile']).data
            })
        
        return {
            "success": True,
            "message": "Users retrieved successfully",
            "data": {
                "users": serialized_users
            },
            "status_code": status.HTTP_200_OK
        }

    @staticmethod
    def change_password(user: User, data: dict):
        serializer = ChangePasswordSerializer(data=data, context={"user": user})
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return {
                "success": True,
                "message": "Password changed successfully",
                "data": {},
                "status_code": status.HTTP_200_OK
            }
        return {
            "success": False,
            "message": "Invalid input",
            "data": serializer.errors,
            "status_code": status.HTTP_400_BAD_REQUEST
        }