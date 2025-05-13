from django.core.exceptions import ValidationError
from rest_framework import status
from django.contrib.auth.models import User
from accounts.models import Profile
from gas_stock_management.response import RepositoryResponse
import re


class AccountRepository:
    @staticmethod
    def _validate_phone_number(phone: str) -> bool:
        regex = r'^\+?\d{10,15}$'
        return re.match(regex, phone) is not None

    @staticmethod
    def _is_valid_role(role: str) -> bool:
        return role in dict(Profile.ROLE_CHOICES)

    @staticmethod
    def _check_uniqueness(username: str, email: str, phone_number: str = None) -> None:
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        if phone_number and Profile.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("Phone number already exists")

    @staticmethod
    def create_user(username: str, email: str, password: str, role: str = 'customer', phone_number: str = None, **extra_fields):
     try:
        # Check for existing username
        if User.objects.filter(username=username).exists():
            return RepositoryResponse(
                success=False,
                message="Username already exists",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        # Check for existing email
        if User.objects.filter(email=email).exists():
            return RepositoryResponse(
                success=False,
                message="Email already exists", 
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        # Check for existing phone number
        if phone_number and Profile.objects.filter(phone_number=phone_number).exists():
            return RepositoryResponse(
                success=False,
                message="Phone number already exists",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Validate role
        if role not in dict(Profile.ROLE_CHOICES).keys():
            return RepositoryResponse(
                success=False,
                message="Invalid role",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Validate phone format
        if phone_number and not AccountRepository._validate_phone_number(phone_number):
            return RepositoryResponse(
                success=False,
                message="Invalid phone number format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Create user if all validations pass
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )
        
        # Set profile fields
        user.profile.role = role
        user.profile.phone_number = phone_number
        user.profile.save()

        return RepositoryResponse(
            success=True,
            data={"user": user, "profile": user.profile},
            status_code=status.HTTP_201_CREATED
        )

     except Exception as e:
        return RepositoryResponse(
            success=False,
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @staticmethod
    def get_user_by_id(user_id: int) -> RepositoryResponse:
     try:
        user = User.objects.select_related('profile').get(id=user_id)
        return RepositoryResponse(
            success=True,
            data={"user": user, "profile": user.profile},
            status_code=status.HTTP_200_OK  # 200 for successful retrieval
        )
     except User.DoesNotExist:
        return RepositoryResponse(
            success=False,
            message="User not found",
            status_code=status.HTTP_404_NOT_FOUND  # 404 for not found
        )
     except Exception as e:
        return RepositoryResponse(
            success=False,
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @staticmethod
    def get_users_by_role(role: str) -> RepositoryResponse:
        try:
            if role not in dict(Profile.ROLE_CHOICES).keys():
                return RepositoryResponse(
                    success=False,
                    message="Invalid role",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            users = User.objects.filter(profile__role=role).select_related('profile')
            users_data = [{"user": user, "profile": user.profile} for user in users]

            return RepositoryResponse(
                success=True,
                data={"users": users_data},
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return RepositoryResponse(
                success=False,
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @staticmethod
    def update_profile(user_id: int, phone_number: str = None, address: str = None, role: str = None, profile_image: str = None) -> RepositoryResponse:
        try:
            profile = Profile.objects.get(user_id=user_id)

            if phone_number and not AccountRepository._validate_phone_number(phone_number):
                return RepositoryResponse(False, "Invalid phone number format", status.HTTP_400_BAD_REQUEST)

            if role and not AccountRepository._is_valid_role(role):
                return RepositoryResponse(False, "Invalid role", status.HTTP_400_BAD_REQUEST)

            if phone_number:
                profile.phone_number = phone_number
            if address:
                profile.address = address
            if role:
                profile.role = role
            if profile_image:
                profile.profile_image = profile_image

            profile.save()

            return RepositoryResponse(
                success=True, 
                data={"profile": profile}, 
                status_code=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return RepositoryResponse(
                success=False,
                message= "Profile not found", 
                status_code=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return RepositoryResponse(
                success=False, 
                message= str(e), 
                status_code= status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def delete_user_by_id(user_id: int) -> RepositoryResponse:
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return RepositoryResponse(
                success= True, 
                message="User deleted successfully", 
                status_code= status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return RepositoryResponse(
                success= False, 
                message="User not found", 
                status_code=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return RepositoryResponse(
                success=False,
                message=str(e), 
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
