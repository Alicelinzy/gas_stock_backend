from django.core.exceptions import ValidationError
from rest_framework import status
from django.contrib.auth.models import User
from accounts.models import Profile
from gas_stock_management.response import RepositoryResponse
import re

class AccountRepository:
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate phone format (e.g., +250123456789 or 0123456789)"""
        regex = r'^\+?\d{10,15}$'
        return re.match(regex, phone) is not None

    @classmethod
    def _check_uniqueness(cls, username: str, email: str, phone_number: str = None) -> None:
        """Raises ValidationError if email, username, or phone number already exist."""
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        if phone_number and Profile.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("Phone number already exists")

    @classmethod
    def create_user(cls, username: str,email: str, password: str,role: str = 'customer',
        phone_number: str = None,
        **extra_fields
    ) -> RepositoryResponse:
        try:
            # Validate uniqueness
            cls._check_uniqueness(username, email, phone_number)

            # Validate role
            if role not in dict(Profile.ROLE_CHOICES).keys():
                return RepositoryResponse(
                    success=False,
                    message="Invalid role",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Validate phone (if provided)
            if phone_number and not cls.validate_phone_number(phone_number):
                return RepositoryResponse(
                    success=False,
                    message="Invalid phone number format",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                **extra_fields
            )
            # Profile is auto-created via signal
            user.profile.role = role
            user.profile.phone_number = phone_number
            user.profile.save()

            return RepositoryResponse(
                success=True,
                data={"user": user, "profile": user.profile},
                status_code=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return RepositoryResponse(
                success=False,
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return RepositoryResponse(
                success=False,
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @classmethod
    def get_user_by_id(cls, user_id: int) -> RepositoryResponse:
        """Get a user by their ID."""
        try:
            user = User.objects.select_related('profile').get(id=user_id)
            return RepositoryResponse(
                success=True,
                data={"user": user, "profile": user.profile},
                status_code=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return RepositoryResponse(
                success=False,
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return RepositoryResponse(
                success=False,
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @classmethod
    def get_users_by_role(cls, role: str) -> RepositoryResponse:
        """Get all users with a specific role."""
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
   
    @classmethod
    def update_profile(
        cls,
        user_id: int,
        phone_number: str = None,
        address: str = None,
        role: str = None,
        profile_image: str = None
    ) -> RepositoryResponse:
        try:
            profile = Profile.objects.get(user_id=user_id)

            if phone_number and not cls.validate_phone_number(phone_number):
                return RepositoryResponse(
                    success=False,
                    message="Invalid phone number format",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            if role and role not in dict(Profile.ROLE_CHOICES).keys():
                return RepositoryResponse(
                    success=False,
                    message="Invalid role",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Update fields only if provided
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
                status_code=status.HTTP_200_OK
            )
        except Profile.DoesNotExist:
            return RepositoryResponse(
                success=False,
                message="Profile not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return RepositoryResponse(
                success=False,
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @classmethod
    def delete_user_by_id(cls, user_id: int) -> RepositoryResponse:
        """Delete a user by their ID."""
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return RepositoryResponse(
                success=True,
                message="User deleted successfully",
                status_code=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return RepositoryResponse(
                success=False,
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return RepositoryResponse(
                success=False,
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )