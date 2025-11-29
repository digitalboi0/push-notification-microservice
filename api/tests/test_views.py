from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import App, Device, Template
import json


class NotificationViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.app = App.objects.create(name='Test App')
        self.app_key = self.app.app_key
        
        # Add app key to all requests
        self.client.defaults['HTTP_X_APP_KEY'] = self.app_key

    def test_send_notification_success(self):
        # Create a template
        Template.objects.create(
            app=self.app,
            name='welcome',
            title_template='Welcome {user.name}!',
            body_template='Hello {user.name}, welcome!',
            is_active=True
        )
        
        data = {
            'notification_type': 'welcome',
            'device_token': 'test_device_token',
            'platform': 'android',
            'user': {
                'name': 'John Doe',
                'email': 'john@example.com'
            },
            'data': {
                'custom_field': 'custom_value'
            }
        }
        
        response = self.client.post(
            reverse('send-notification'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(response.data['success'])

    def test_send_notification_with_direct_title_body(self):
        data = {
            'notification_type': 'custom',
            'device_token': 'test_device_token',
            'platform': 'android',
            'user': {
                'name': 'John Doe'
            },
            'title': 'Custom Title',
            'body': 'Custom Body'
        }
        
        response = self.client.post(
            reverse('send-notification'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(response.data['success'])

    def test_send_notification_invalid_app_key(self):
        self.client.defaults['HTTP_X_APP_KEY'] = 'invalid_key'
        
        data = {
            'notification_type': 'welcome',
            'device_token': 'test_device_token',
            'platform': 'android',
            'user': {
                'name': 'John Doe'
            }
        }
        
        response = self.client.post(
            reverse('send-notification'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_send_notification_missing_template(self):
        data = {
            'notification_type': 'nonexistent_template',
            'device_token': 'test_device_token',
            'platform': 'android',
            'user': {
                'name': 'John Doe'
            }
        }
        
        response = self.client.post(
            reverse('send-notification'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])