from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid


class App(models.Model):
    """
    Represents an application that can send push notifications.
    Each app has its own credentials and templates.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    app_key = models.CharField(
        max_length=64, 
        unique=True, 
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message='App key can only contain letters, numbers, and underscores'
            )
        ]
    )
    description = models.TextField(blank=True)
    fcm_server_key = models.TextField(blank=True, help_text="Firebase Server Key")
    apns_cert_path = models.TextField(blank=True, help_text="Path to APNs certificate")
    apns_topic = models.CharField(max_length=255, blank=True, help_text="APNs topic for push notifications")
    web_vapid_public_key = models.TextField(blank=True, help_text="Web VAPID public key")
    web_vapid_private_key = models.TextField(blank=True, help_text="Web VAPID private key")
    is_active = models.BooleanField(default=True)
    rate_limit = models.IntegerField(default=1000, help_text="Max notifications per minute")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'push_apps'
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'

    def __str__(self):
        return self.name