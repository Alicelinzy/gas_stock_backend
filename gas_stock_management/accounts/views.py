from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.contrib.auth import logout
from accounts.services.accounts_services import AccountService
from .permissions import IsAdmin, IsManager
from accounts.serializers import RegisterSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'User registered successfully'}, 
                status=status.HTTP_201_CREATED)
        
        return Response({
            "success": False,
            "message": "Invalid input",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        service_response = AccountService.login_user(request.data)
        status_code = service_response.get("status_code", status.HTTP_200_OK)
        
        # If login successful, flatten the token structure
        if service_response.get('success'):
            response_data = {
                'access': service_response['data']['tokens']['access'],
                'refresh': service_response['data']['tokens']['refresh'],
                'user': service_response['data']['user']
            }
            return Response(
                response_data, 
                status=status_code)
        
        return Response(
            service_response, 
            status=status_code)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({
            "success": True,
            "message": "Logged out successfully",
            "data": {}
        }, status=status.HTTP_200_OK)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        if user_id and not self._can_view_profile(request.user, user_id):
            return self._unauthorized_response()
        
        try:
            service_response = AccountService.get_user_profile(user_id or request.user.id)
            status_code = service_response.get("status_code", status.HTTP_200_OK)
            return Response(service_response, status=status_code)
        except Exception as e:
            return Response({
                "success": False,
                "message": "Failed to fetch profile",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def _can_view_profile(self, user, target_user_id):
        return (user.id == target_user_id or 
                user.is_staff or 
                user.profile.role in ['admin', 'manager'])

    def _unauthorized_response(self):
        return Response({
            "success": False,
            "message": "Unauthorized access",
            "data": {}
        }, status=status.HTTP_403_FORBIDDEN)

class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, user_id=None):
        if user_id and not self._can_modify_profile(request.user, user_id):
            return self._unauthorized_response()
        
        service_response = AccountService.update_profile(
            user_id or request.user.id, 
            request.data
        )
        return Response(service_response, status=service_response.get("status_code", status.HTTP_200_OK))
    def _can_modify_profile(self, user, target_user_id):
            return (user.id == target_user_id or 
                user.is_staff or 
                user.profile.role == 'admin')

    def _unauthorized_response(self):
        return Response({
            "success": False,
            "message": "Unauthorized access",
            "data": {}
        }, status=status.HTTP_403_FORBIDDEN)

    def _can_modify_profile(self, user, target_user_id):
        return (user.id == target_user_id or 
                user.is_staff or 
                user.profile.role == 'admin')

    def _unauthorized_response(self):
        return Response({
            "success": False,
            "message": "Unauthorized access",
            "data": {}
        }, status=status.HTTP_403_FORBIDDEN)

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, user_id):
        if request.user.id == user_id:
            return Response({
                "success": False,
                "message": "Cannot delete your own account",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service_response = AccountService.delete_user(user_id)
            status_code = service_response.get("status_code", status.HTTP_200_OK)
            return Response(service_response, status=status_code)
        except Exception as e:
            return Response({
                "success": False,
                "message": "Failed to delete user",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            service_response = AccountService.change_password(request.user, request.data)
            status_code = service_response.get("status_code", status.HTTP_200_OK)
            return Response(service_response, status=status_code)
        except Exception as e:
            return Response({
                "success": False,
                "message": "Failed to change password",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class UsersByRoleView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        try:
            service_response = AccountService.get_users_by_role(
                request.query_params.get('role', 'customer')
            )
            status_code = service_response.get("status_code", status.HTTP_200_OK)
            return Response(service_response, status=status_code)
        except Exception as e:
            return Response({
                "success": False,
                "message": "Failed to fetch users",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)