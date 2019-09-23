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
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class TestUserModelCase(unittest.TestCase):


    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.user = {
            'username': 'test_username',
            'email': 'test_email@test.com',
            'password': 'asdfasdf'
        }
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    def test_user_creation(self):
        # Test POST user creation
        res = self.client.post('/api/v1/register', data=json.dumps(self.user), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        self.assertIn('test_username', str(res.data))


    def test_user_update(self):
        # TEST PUT user update
        user_data = json.loads(self.client.post(
            '/api/v1/register',
            data=json.dumps(self.user),
            content_type='application/json'
        ).data)
        token = json.loads(self.client.post(
            'api/v1/login',
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


    def test_delete_user(self):
        # Test DELETE Call
        self.assertEqual(0, User.query.count())
        # Create a user
        user_data = json.loads(self.client.post(
            '/api/v1/register',
            data=json.dumps(self.user),
            content_type='application/json'
        ).data)
        token = json.loads(self.client.post(
            'api/v1/login',
            headers={
                'Authorization': _basic_auth_str(self.user['username'], self.user['password'])
            }
        ).data)['token']
        self.assertEqual(1, User.query.count())
        # Try to delete with different user and assert that it is not deleted
        user_2 = self.user.copy()
        user_2['username'] = 'test_username2'
        user_2['email'] = 'test_email2@test.com'
        user_2_data = json.loads(self.client.post(
            '/api/v1/register',
            data=json.dumps(user_2),
            content_type='application/json'
        ).data)
        self.assertEqual(2, User.query.count())
        token_2 = json.loads(self.client.post(
            'api/v1/login',
            headers={
                'Authorization': _basic_auth_str(user_2['username'], self.user['password'])
            }
        ).data)['token']
        bad_req = self.client.delete(
            '/api/v1/users/{}'.format(user_data['id']),
            content_type='application/json',
            headers={
                'Authorization': 'Bearer {}'.format(token_2)
            }
        )
        self.assertEqual(2, User.query.count())
        self.assertEqual(bad_req.status_code, 400)
        # Try to delete user with itself and assert true
        res = self.client.delete(
            '/api/v1/users/{}'.format(user_data['id']),
            content_type='application/json',
            headers={
                'Authorization': 'Bearer {}'.format(token)
            }
        )
        # Now only user 2 should be left
        self.assertEqual(1, User.query.count())
        self.assertEqual(res.status_code, 204)
