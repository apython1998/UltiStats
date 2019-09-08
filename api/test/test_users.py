#!/usr/bin/env python
from datetime import datetime, timedelta
from requests.auth import _basic_auth_str
import unittest
import json
from app import create_app, db
from app.models import User
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class TestUserModelCase(unittest.TestCase):


    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.user = {
            'username': 'test_username',
            'email': 'test_email@test.com',
            'password': 'asdfasdf'
        }
        # binds app to current_context
        with self.app.app_context():
            # Create all the tables
            db.create_all()


    def test_user_creation(self):
        # Test POST user creation
        res = self.client.post('/api/v1/users', data=json.dumps(self.user), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        self.assertIn('test_username', str(res.data))


    def test_user_update(self):
        # TEST PUT user update
        user_data = json.loads(self.client.post(
            '/api/v1/users',
            data=json.dumps(self.user),
            content_type='application/json'
        ).data)
        token = json.loads(self.client.post(
            'api/tokens',
            headers={
                'Authorization': _basic_auth_str(self.user['username'], self.user['password'])
            }
        ).data)['token']
        update_data = {
            'username': 'new_test',
            'email': 'new_email@email.com'
        }
        res = self.client.put(
            '/api/v1/users/{}'.format(user_data['id']),
            data=json.dumps(update_data),
            content_type='application/json',
            headers={
                'Authorization': 'Bearer {}'.format(token)
            }
        )
        updated_user = json.loads(res.data)
        self.assertEqual('new_test', updated_user['username'])
        self.assertEqual('new_email@email.com', updated_user['email'])
        self.assertEqual(1, updated_user['id'])


    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()
