#!/usr/bin/env python
from datetime import datetime, timedelta
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


    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()
