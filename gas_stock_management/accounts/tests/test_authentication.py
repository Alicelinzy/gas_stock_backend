from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Profile
from rest_framework.test import APIClient

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Clean up any existing users and profiles
        User.objects.all().delete()
        Profile.objects.all().delete()

        # Test data for registration
        self.registration_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword123",
            "role": "customer"
        }
        
        # Create test users for different scenarios
        self.test_user = User.objects.create_user(
            username="existinguser", 
            password="existingpass",
            email="existing@example.com"
        )
        
        # Create admin user for admin-only endpoints
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.admin.profile.role = 'admin'
        self.admin.profile.save()
        
        # Create URLs for tests
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.change_password_url = reverse('change-password')
        self.token_url = reverse('token_obtain_pair')
        self.token_refresh_url = reverse('token_refresh')

    def test_register_valid_user(self):
        """Test that a valid user can be registered"""
        response = self.client.post(self.register_url, self.registration_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        
        # Verify profile creation
        user = User.objects.get(username='testuser')
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.role, 'customer')

    def test_register_duplicate_username(self):
        """Test registration with existing username fails"""
        duplicate_data = self.registration_data.copy()
        duplicate_data['username'] = 'existinguser'  # Username that already exists
        
        response = self.client.post(self.register_url, duplicate_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data.get('errors', {}))

    def test_register_invalid_email(self):
        """Test registration with invalid email fails"""
        invalid_data = self.registration_data.copy()
        invalid_data['email'] = 'not-an-email'
        
        response = self.client.post(self.register_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data.get('errors', {}))

    def test_login_valid_credentials(self):
        """Test login with valid credentials returns token"""
        response = self.client.post(
            self.login_url, 
            {"username": "existinguser", "password": "existingpass"}, 
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials fails"""
        response = self.client.post(
            self.login_url, 
            {"username": "existinguser", "password": "wrongpassword"}, 
            format='json'
        )
        
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_logout(self):
        """Test authenticated user can logout"""
        self.client.force_authenticate(user=self.test_user)
        response = self.client.post(self.logout_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            "success": True,
            "message": "Logged out successfully",
            "data": {}
        })

    def test_change_password_success(self):
        """Test authenticated user can change password"""
        self.client.force_authenticate(user=self.test_user)
        response = self.client.post(
            self.change_password_url,
            {
                "old_password": "existingpass",
                "new_password": "newpassword123"
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the password was actually changed by trying to login
        self.client.logout()
        login_response = self.client.post(
            self.login_url, 
            {"username": "existinguser", "password": "newpassword123"}, 
            format='json'
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_change_password_wrong_old_password(self):
        """Test change password fails with wrong old password"""
        self.client.force_authenticate(user=self.test_user)
        response = self.client.post(
            self.change_password_url,
            {
                "old_password": "wrongpassword",
                "new_password": "newpassword123"
            },
            format='json'
        )
        
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_unauthenticated(self):
        """Test change password endpoint requires authentication"""
        # No authentication
        response = self.client.post(
            self.change_password_url,
            {
                "old_password": "existingpass",
                "new_password": "newpassword123"
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_endpoint(self):
        """Test direct JWT token endpoint works"""
        response = self.client.post(
            self.token_url,
            {
                "username": "existinguser",
                "password": "existingpass"
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_refresh_endpoint(self):
        """Test token refresh endpoint works"""
        # First get a token
        token_response = self.client.post(
            self.token_url,
            {
                "username": "existinguser",
                "password": "existingpass"
            },
            format='json'
        )
        
        # Then try to refresh it
        refresh_response = self.client.post(
            self.token_refresh_url,
            {
                "refresh": token_response.data['refresh']
            },
            format='json'
        )
        
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

    def test_token_refresh_invalid_token(self):
        """Test token refresh fails with invalid token"""
        refresh_response = self.client.post(
            self.token_refresh_url,
            {
                "refresh": "invalid-token"
            },
            format='json'
        )
        
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_with_valid_token(self):
        """Test accessing protected endpoint with valid token"""
        # First login to get token
        login_response = self.client.post(
            self.login_url,
            {"username": "existinguser", "password": "existingpass"},
            format='json'
        )
        
        # Set the token in the header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
        
        # Access a protected endpoint (profile in this case)
        profile_url = reverse('my-profile')
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token fails"""
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid-token")
        
        profile_url = reverse('my-profile')
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)