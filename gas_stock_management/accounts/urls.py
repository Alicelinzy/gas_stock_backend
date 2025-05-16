from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, ProfileView, UpdateProfileView,
    DeleteUserView, ChangePasswordView, UsersByRoleView
)

urlpatterns = [
   path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    
    path('profile/', ProfileView.as_view(), name='my-profile'),
    path('profile/<int:user_id>/', ProfileView.as_view(), name='user-profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update-my-profile'),
    path('profile/update/<int:user_id>/', UpdateProfileView.as_view(), name='update-user-profile'),
    
    path('user/delete/<int:user_id>/', DeleteUserView.as_view(), name='delete-user'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('users/', UsersByRoleView.as_view(), name='users-by-role'),
]