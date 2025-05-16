from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import Profile
from accounts.repository.accounts_repository import AccountRepository
from django.core.exceptions import ValidationError
from rest_framework import status

class AccountRepositoryTest(TestCase):
    def setUp(self):
        # Create test users
        self.admin = User.objects.create_user(
            username='admin', 
            email='admin@test.com', 
            password='adminpass'
        )
        self.admin.profile.role = 'admin'
        self.admin.profile.save()

        self.customer = User.objects.create_user(
            username='customer1', 
            email='customer1@test.com', 
            password='customerpass',
        )
        self.customer.profile.phone_number = '+250788123456'
        self.customer.profile.save()

    # === CREATE USER TESTS ===
    def test_create_user_success(self):
        response = AccountRepository.create_user(
            username='newuser',
            email='new@test.com',
            password='testpass123',
            role='customer',
            phone_number='+250789123456'
        )
        
        self.assertTrue(response.success)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 3)
        
        user = User.objects.get(username='newuser')
        self.assertEqual(user.profile.role, 'customer')
        self.assertEqual(user.profile.phone_number, '+250789123456')

    def test_create_user_duplicate_username(self):
  
       response = AccountRepository.create_user(
        username='customer1',  # duplicate from setUp()
        email='new@test.com',
        password='testpass123'
    )
    
    # Should return failure response
       self.assertFalse(response.success)
       self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
       self.assertEqual(response.message, "Username already exists")
    
    # Verify no new user was created
       self.assertEqual(User.objects.count(), 2)  # Only admin and customer1 should exist

    def test_create_user_invalid_phone(self):
        response = AccountRepository.create_user(
            username='newuser',
            email='new@test.com',
            password='testpass123',
            phone_number='invalid'
        )
        
        self.assertFalse(response.success)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.message, 'Invalid phone number format')

    # # === GET USER TESTS ===
    def test_get_user_by_id_success(self):
        response = AccountRepository.get_user_by_id(self.customer.id)
        
        self.assertTrue(response.success)
        self.assertEqual(response.data['user'].username, 'customer1')
        self.assertEqual(response.data['profile'].phone_number, '+250788123456')

    def test_get_user_not_found(self):
    # Try to get non-existent user
        response = AccountRepository.get_user_by_id(9999)
    
    # Should return failure response
        self.assertFalse(response.success)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.message, "User not found")


    # # === GET USERS BY ROLE TESTS ===
    def test_get_users_by_role_success(self):
        # Create another customer
        User.objects.create_user(username='customer2', email='c2@test.com', password='testpass')
        
        response = AccountRepository.get_users_by_role('customer')
        
        self.assertTrue(response.success)
        self.assertEqual(len(response.data['users']), 2)
        self.assertEqual(response.data['users'][0]['user'].username, 'customer1')

    def test_get_users_invalid_role(self):
        response = AccountRepository.get_users_by_role('invalid_role')

        self.assertFalse(response.success)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.message, "Invalid role")

    # # === UPDATE PROFILE TESTS ===
    def test_update_profile_success(self):
        response = AccountRepository.update_profile(
            user_id=self.customer.id,
            phone_number='+250788654321',
            role='delivery'
        )
        
        self.assertTrue(response.success)
        updated_profile = Profile.objects.get(user=self.customer)
        self.assertEqual(updated_profile.phone_number, '+250788654321')
        self.assertEqual(updated_profile.role, 'delivery')

    def test_update_profile_not_found(self):
        response = AccountRepository.update_profile(
            user_id=9999,
            phone_number='+250788654321'
        )
        
        self.assertFalse(response.success)
        self.assertEqual(response.status_code, 404)

    # # === DELETE USER TESTS ===
    def test_delete_user_success(self):
        user_id = self.customer.id
        response = AccountRepository.delete_user_by_id(user_id)
        
        self.assertTrue(response.success)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=user_id)
        self.assertEqual(User.objects.count(), 1)

    def test_delete_user_not_found(self):
        response = AccountRepository.delete_user_by_id(9999)
        
        self.assertFalse(response.success)
        self.assertEqual(response.status_code, 404)