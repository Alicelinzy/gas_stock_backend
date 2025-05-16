
from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Profile
from rest_framework.test import APIClient

class AccountTests(TestCase):

    def setUp(self):
        self.client = APIClient()
    # Clean up any existing users and profiles
        User.objects.all().delete()
        Profile.objects.all().delete()

        self.customer_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword123",
        "role": "customer"
    }
    
    # Create admin user for tests that need it
        self.admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass'
    )
    # Set admin role if your system requires it
        self.admin.profile.role = 'admin'
        self.admin.profile.save()

    def test_register_user(self):
        url = reverse('register')  
        response = self.client.post(url, self.customer_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username=self.customer_data['username'])
        self.assertEqual(user.email, self.customer_data['email'])

        # Check if profile was created
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.role, self.customer_data['role'])


    def test_login_user(self):

        user = User.objects.create_user(
        username="loginuser", 
        password="testpass123",
        email="loginuser@test.com"  # Add email if your User model requires it
    )
    
        url = reverse("login")
        response = self.client.post(url, {
        "username": "loginuser",
        "password": "testpass123"
    }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    # Verify token structure based on your actual API response:
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    # Verify user data if needed
        self.assertIn("user", response.data)  


    def test_logout_user(self):
        # Authenticate using DRF's client
        self.client.force_authenticate(user=self.admin)
        
        url = reverse("logout")
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            "success": True,
            "message": "Logged out successfully",
            "data": {}
        })

    def test_get_own_profile(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("my-profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("success"))

    def test_update_own_profile(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("update-my-profile")
        data = {"address": "Kigali", "phone_number": "0799999999"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("change-password")
        data = {"old_password": "adminpass", "new_password": "newsecurepass123"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_users_by_role_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("users-by-role") + "?role=customer"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        user_to_delete = User.objects.create_user(username="deleteuser", password="pass123")
        url = reverse("delete-user", kwargs={"user_id": user_to_delete.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_delete_own_account(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("delete-user", kwargs={"user_id": self.admin.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
