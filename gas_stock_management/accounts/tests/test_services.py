from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import Profile
from accounts.services.accounts_services import AccountService  # Assuming your service is in 'services' module
from rest_framework import status

class AccountServiceTest(TestCase):
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
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'testpass123',
            'role': 'customer',
            'phone_number': '+250789123456'
        }
        
        response = AccountService.register_user(data)
        
        self.assertTrue(response['success'])
        self.assertEqual(response['status_code'], 201)  # Expecting success status code for creation
        self.assertEqual(User.objects.count(), 3)  # Should be 3 users now: admin, customer1, and newuser
        
        user = User.objects.get(username='newuser')
        self.assertEqual(user.profile.role, 'customer')
        self.assertEqual(user.profile.phone_number, '+250789123456')

    def test_create_user_duplicate_username(self):
        data = {
            'username': 'customer1',  # Duplicate username from setUp()
            'email': 'new@test.com',
            'password': 'testpass123',
            'role': 'customer',
            'phone_number': '+250789123456'
        }
        
        response = AccountService.register_user(data)
        
        # Should return failure response indicating the username already exists
        self.assertFalse(response['success'])
        self.assertEqual(response['status_code'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response['message'], "Invalid input")
        
        # Verify no new user was created
        self.assertEqual(User.objects.count(), 2) # Only admin and customer1 should exist


    def test_create_user_invalid_phone(self):
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'testpass123',
            'phone_number': 'invalid'  # Invalid phone number format
        }
        
        response = AccountService.register_user(data)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['status_code'], status.HTTP_400_BAD_REQUEST)  # Invalid input
        self.assertEqual(response['message'], 'Invalid phone number format')

    # # # === GET USER TESTS ===
    def test_get_user_by_id_success(self):
        response = AccountService.get_user_profile(self.customer.id)
        
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['user']['username'], 'customer1')
        self.assertEqual(response['data']['profile']['phone_number'], '+250788123456')

    def test_get_user_not_found(self):
        response = AccountService.get_user_profile(9999)  # Non-existent user ID
        
        self.assertFalse(response['success'])
        self.assertEqual(response['status_code'], status.HTTP_404_NOT_FOUND)
        self.assertEqual(response['message'], "User not found")

    # # # === GET USERS BY ROLE TESTS ===
    def test_get_users_by_role_success(self):
    # Create another customer
     User.objects.create_user(username='customer2', email='c2@test.com', password='testpass')
     response = AccountService.get_users_by_role('customer')
     self.assertTrue(response['success'])
     self.assertEqual(len(response['data']['users']), 2)  # 2 users with role 'customer'

     usernames = [user_data['user']['username'] for user_data in response['data']['users']]
     self.assertIn('customer1', usernames)
     self.assertIn('customer2', usernames)

   
    def test_get_users_invalid_role(self):
        response = AccountService.get_users_by_role('invalid_role')
        
        self.assertFalse(response['success'])
        self.assertEqual(response['status_code'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response['message'], "Invalid role")

    # # === UPDATE PROFILE TESTS ===
    def test_update_profile_success(self):
        update_data = {
        'phone_number': '+250788654321',
        'role': 'delivery'
    }
        response = AccountService.update_profile(
            user_id=self.customer.id,
              data=update_data  # Pass data as a dictionary
    )
    
        self.assertTrue(response['success'])
        updated_profile = Profile.objects.get(user=self.customer)
        self.assertEqual(updated_profile.phone_number, '+250788654321')
        self.assertEqual(updated_profile.role, 'delivery')

    def test_update_profile_not_found(self):
        update_data = {
        'phone_number': '+250788654321',
    }
        response = AccountService.update_profile(
            user_id=9999,
            data=update_data
        )
        
        self.assertFalse(response['success'])
        self.assertEqual(response['status_code'], status.HTTP_404_NOT_FOUND)

    # # === DELETE USER TESTS ===
    def test_delete_user_success(self):
        user_id = self.customer.id
        response = AccountService.delete_user(user_id)
        
        self.assertTrue(response['success'])
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=user_id)
        self.assertEqual(User.objects.count(), 1)  # Only admin should remain

    def test_delete_user_not_found(self):
        response = AccountService.delete_user(9999)  # Non-existent user ID
        
        self.assertFalse(response['success'])
        self.assertEqual(response['status_code'], status.HTTP_404_NOT_FOUND)
