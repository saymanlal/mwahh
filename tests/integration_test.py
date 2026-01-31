#!/usr/bin/env python
import os
import django
import json
import requests
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import User as ApiUser, InstituteDomain, Match, ChatRoom
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

API_BASE = os.environ.get('API_URL', 'http://localhost:8000')

class IntegrationTester:
    def __init__(self):
        self.client = APIClient()
        self.test_email1 = 'test1@iit.ac.in'
        self.test_email2 = 'test2@iit.ac.in'
        self.test_password = 'TestPassword123!'
        self.user1_token = None
        self.user2_token = None
        self.user1 = None
        self.user2 = None
        self.match = None

    def print_step(self, step_name, status='OK'):
        color = '\033[92m' if status == 'OK' else '\033[91m'
        reset = '\033[0m'
        print(f'{color}[{status}]{reset} {step_name}')

    def print_error(self, message):
        print(f'\033[91m[ERROR]\033[0m {message}')

    def test_auth_flow(self):
        print('\n=== Testing Authentication Flow ===')
        
        try:
            # 1. Register user 1
            response = self.client.post(
                f'{API_BASE}/api/auth/register/',
                {
                    'email': self.test_email1,
                    'password': self.test_password,
                },
                format='json'
            )
            
            if response.status_code != 201:
                self.print_error(f'Registration failed: {response.data}')
                return False
            
            self.print_step('User 1 registration', 'OK')
            
            # 2. Get OTP from database (in production, this comes via email)
            user = ApiUser.objects.get(email=self.test_email1)
            from api.models import OtpToken
            otp = OtpToken.objects.filter(email=self.test_email1).latest('created_at')
            
            # 3. Verify OTP
            response = self.client.post(
                f'{API_BASE}/api/auth/verify-otp/',
                {
                    'email': self.test_email1,
                    'otp': otp.token,
                },
                format='json'
            )
            
            if response.status_code != 200:
                self.print_error(f'OTP verification failed: {response.data}')
                return False
            
            self.print_step('User 1 OTP verification', 'OK')
            
            # 4. Login and get tokens
            response = self.client.post(
                f'{API_BASE}/api/auth/token/',
                {
                    'email': self.test_email1,
                    'password': self.test_password,
                },
                format='json'
            )
            
            if response.status_code != 200:
                self.print_error(f'Login failed: {response.data}')
                return False
            
            self.user1_token = response.data['access']
            self.user1 = user
            self.print_step('User 1 login and token generation', 'OK')
            
            # 5. Register and setup user 2
            response = self.client.post(
                f'{API_BASE}/api/auth/register/',
                {
                    'email': self.test_email2,
                    'password': self.test_password,
                },
                format='json'
            )
            
            self.print_step('User 2 registration', 'OK')
            
            user2 = ApiUser.objects.get(email=self.test_email2)
            otp2 = OtpToken.objects.filter(email=self.test_email2).latest('created_at')
            
            response = self.client.post(
                f'{API_BASE}/api/auth/verify-otp/',
                {
                    'email': self.test_email2,
                    'otp': otp2.token,
                },
                format='json'
            )
            
            self.print_step('User 2 OTP verification', 'OK')
            
            response = self.client.post(
                f'{API_BASE}/api/auth/token/',
                {
                    'email': self.test_email2,
                    'password': self.test_password,
                },
                format='json'
            )
            
            self.user2_token = response.data['access']
            self.user2 = user2
            self.print_step('User 2 login', 'OK')
            
            return True
            
        except Exception as e:
            self.print_error(f'Auth flow failed: {str(e)}')
            return False

    def test_profile_setup(self):
        print('\n=== Testing Profile Setup ===')
        
        try:
            headers = {'Authorization': f'Bearer {self.user1_token}'}
            
            profile_data = {
                'gender': 'M',
                'age': 22,
                'height_cm': 180,
                'bio': 'Test user 1',
                'degree_or_profession': 'B.Tech Computer Science',
                'interests': ['coding', 'gaming', 'reading'],
                'city': 'Delhi',
                'state': 'Delhi',
                'scope': 'same_institute',
                'preference_mode': 'friend',
            }
            
            response = self.client.patch(
                f'{API_BASE}/api/profile/update/',
                profile_data,
                format='json',
                HTTP_AUTHORIZATION=headers['Authorization']
            )
            
            if response.status_code not in [200, 202]:
                self.print_error(f'Profile update failed: {response.data}')
                return False
            
            self.print_step('User 1 profile setup', 'OK')
            
            # Setup user 2
            headers = {'Authorization': f'Bearer {self.user2_token}'}
            profile_data['gender'] = 'F'
            profile_data['bio'] = 'Test user 2'
            
            response = self.client.patch(
                f'{API_BASE}/api/profile/update/',
                profile_data,
                format='json',
                HTTP_AUTHORIZATION=headers['Authorization']
            )
            
            self.print_step('User 2 profile setup', 'OK')
            return True
            
        except Exception as e:
            self.print_error(f'Profile setup failed: {str(e)}')
            return False

    def test_matching(self):
        print('\n=== Testing Matching System ===')
        
        try:
            headers = {'Authorization': f'Bearer {self.user1_token}'}
            
            response = self.client.get(
                f'{API_BASE}/api/matches/',
                HTTP_AUTHORIZATION=headers['Authorization']
            )
            
            if response.status_code != 200:
                self.print_error(f'Match fetching failed: {response.data}')
                return False
            
            matches = response.data.get('results', [])
            self.print_step(f'Fetched {len(matches)} matches', 'OK')
            
            if len(matches) > 0:
                match_uuid = matches[0]['match_uuid']
                
                response = self.client.post(
                    f'{API_BASE}/api/matches/{match_uuid}/accept/',
                    {},
                    format='json',
                    HTTP_AUTHORIZATION=headers['Authorization']
                )
                
                if response.status_code == 200:
                    self.print_step('Match acceptance', 'OK')
                    self.match = matches[0]
            
            return True
            
        except Exception as e:
            self.print_error(f'Matching test failed: {str(e)}')
            return False

    def test_notifications(self):
        print('\n=== Testing Notifications ===')
        
        try:
            headers = {'Authorization': f'Bearer {self.user1_token}'}
            
            response = self.client.get(
                f'{API_BASE}/api/notifications/',
                HTTP_AUTHORIZATION=headers['Authorization']
            )
            
            if response.status_code != 200:
                self.print_error(f'Notification fetch failed')
                return False
            
            notifications = response.data.get('results', [])
            self.print_step(f'Fetched {len(notifications)} notifications', 'OK')
            return True
            
        except Exception as e:
            self.print_error(f'Notification test failed: {str(e)}')
            return False

    def cleanup(self):
        print('\n=== Cleanup ===')
        try:
            ApiUser.objects.filter(email__in=[self.test_email1, self.test_email2]).delete()
            self.print_step('Test users deleted', 'OK')
        except Exception as e:
            self.print_error(f'Cleanup failed: {str(e)}')

    def run_all_tests(self):
        print('\n' + '='*50)
        print('INTEGRATION TEST SUITE')
        print('='*50)
        
        results = {
            'auth': self.test_auth_flow(),
            'profile': self.test_profile_setup(),
            'matching': self.test_matching(),
            'notifications': self.test_notifications(),
        }
        
        print('\n' + '='*50)
        print('TEST RESULTS')
        print('='*50)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test, result in results.items():
            status = '\033[92m✓ PASS\033[0m' if result else '\033[91m✗ FAIL\033[0m'
            print(f'{status} {test}')
        
        print(f'\nTotal: {passed}/{total} passed')
        
        self.cleanup()
        
        return passed == total

if __name__ == '__main__':
    tester = IntegrationTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
