from django.test import TestCase
from django.core.exceptions import ValidationError
from ..models import App, Device, Template, SendLog
import uuid


class AppModelTest(TestCase):
    def setUp(self):
        self.app = App.objects.create(
            name='Test App',
            description='A test application',
            rate_limit=1000
        )

    def test_app_creation(self):
        self.assertEqual(self.app.name, 'Test App')
        self.assertTrue(self.app.app_key)
        self.assertTrue(self.app.is_active)
        self.assertEqual(self.app.rate_limit, 1000)

    def test_app_key_uniqueness(self):
        with self.assertRaises(Exception):
            App.objects.create(
                name='Another App',
                app_key=self.app.app_key  # Use same app_key
            )


class DeviceModelTest(TestCase):
    def setUp(self):
        self.app = App.objects.create(name='Test App')
        self.device = Device.objects.create(
            app=self.app,
            device_token='test_device_token',
            platform='android',
            user_identifier='user123'
        )

    def test_device_creation(self):
        self.assertEqual(self.device.platform, 'android')
        self.assertEqual(self.device.user_identifier, 'user123')
        self.assertTrue(self.device.is_active)

    def test_device_token_normalization(self):
        device = Device.objects.create(
            app=self.app,
            device_token='  test_token_with_spaces  ',
            platform='ios',
            user_identifier='user456'
        )
        self.assertEqual(device.device_token, 'test_token_with_spaces')


class TemplateModelTest(TestCase):
    def setUp(self):
        self.app = App.objects.create(name='Test App')
        self.template = Template.objects.create(
            app=self.app,
            name='welcome',
            title_template='Welcome {user.name}!',
            body_template='Hello {user.name}, welcome to our app!',
            is_active=True
        )

    def test_template_creation(self):
        self.assertEqual(self.template.name, 'welcome')
        self.assertEqual(self.template.title_template, 'Welcome {user.name}!')
        self.assertEqual(self.template.version, 1)

    def test_template_version_increment(self):
        # Create another template with same name
        new_template = Template.objects.create(
            app=self.app,
            name='welcome',
            title_template='Welcome back {user.name}!',
            body_template='Hello again {user.name}!',
            is_active=True
        )
        
        self.assertEqual(new_template.version, 2)
        self.assertEqual(new_template.name, 'welcome')


class SendLogModelTest(TestCase):
    def setUp(self):
        self.app = App.objects.create(name='Test App')
        self.device = Device.objects.create(
            app=self.app,
            device_token='test_token',
            platform='android',
            user_identifier='user123'
        )
        self.template = Template.objects.create(
            app=self.app,
            name='test_template',
            title_template='Test',
            body_template='Test body',
            is_active=True
        )

    def test_send_log_creation(self):
        log = SendLog.objects.create(
            app=self.app,
            device=self.device,
            template=self.template,
            notification_type='test_notification',
            title='Test Title',
            body='Test Body',
            raw_request={'user': {'name': 'Test User'}},
            status='pending'
        )
        
        self.assertEqual(log.notification_type, 'test_notification')
        self.assertEqual(log.status, 'pending')
        self.assertEqual(log.title, 'Test Title')