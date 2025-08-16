import json
from tests.base import BaseTestCase
from app.models import User
from app import db

class AuthTestCase(BaseTestCase):
    def test_register_user(self):
        """Test user registration."""
        response = self.client.post('/api/auth/register',
                                    data=json.dumps({'email': 'test@example.com', 'password': 'password'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('User registered successfully', response.get_data(as_text=True))

    def test_register_existing_user(self):
        """Test registering a user that already exists."""
        user = User(email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/api/auth/register',
                                    data=json.dumps({'email': 'test@example.com', 'password': 'password'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('User already exists', response.get_data(as_text=True))

    def test_login_user(self):
        """Test user login."""
        user = User(email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/api/auth/login',
                                    data=json.dumps({'email': 'test@example.com', 'password': 'password'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        user = User(email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/api/auth/login',
                                    data=json.dumps({'email': 'test@example.com', 'password': 'wrongpassword'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid credentials', response.get_data(as_text=True))
