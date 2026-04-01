from django.test import TestCase, Client
#from django.contrib.auth.models import User
from django.urls import reverse
from wildlife.models import User  # Import your custom User model here


class SignupTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('wildlife:user_signup')  # Replace 'wildlife:user_signup' with your actual URL name

    def test_successful_signup(self):
        response = self.client.post(self.signup_url, {
            'email': 'test@example.com',
            'password': 'testpassword',
            'password_confirm': 'testpassword',
        })
        self.assertEqual(response.status_code, 200)  # Change this to the expected status code after successful signup
        self.assertTemplateUsed(response, 'profile.html')  # Change this to the expected template after successful signup
        # Additional assertions or checks if needed

    def test_password_mismatch(self):
        response = self.client.post(self.signup_url, {
            'email': 'test@example.com',
            'password': 'testpassword',
            'password_confirm': 'mismatchpassword',
        })
        self.assertEqual(response.status_code, 302)  # Change this to the expected status code after password mismatch
        # Additional assertions or checks if needed

    # Add more test cases as needed


class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('wildlife:index')  # Replace 'wildlife:index' with your actual URL name
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')

    def test_successful_login(self):
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'testpassword',
        })
        self.assertEqual(response.status_code, 302)  # Change this to the expected status code after successful login
        self.assertRedirects(response, reverse('wildlife:index'))  # Change this to the expected redirect URL after successful login
        # Additional assertions or checks if needed

    def test_incorrect_credentials(self):
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'incorrectpassword',
        })
        self.assertEqual(response.status_code, 302)  # Change this to the expected status code after incorrect credentials
        # Additional assertions or checks if needed

    # Add more test cases as needed
