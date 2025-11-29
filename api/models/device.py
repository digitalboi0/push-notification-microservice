from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid


class Device(models.Model):
    """
    Represents a device that can receive push notifications.
    """
    PLATFORM_CHOICES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    app = models.ForeignKey('App', on_delete=models.CASCADE, related_name='devices')
    device_token = models.TextField(unique=True, help_text="Push notification token")
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    user_identifier = models.CharField(
        max_length=255,
        help_text="Unique identifier for the user within the app"
    )
    is_active = models.BooleanField(default=True)
    push_token_updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'push_devices'
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'
        unique_together = ['app', 'user_identifier', 'platform']

    def __str__(self):
        return f"{self.app.name} - {self.platform} - {self.user_identifier}"

    def save(self, *args, **kwargs):
        # Normalize device tokens (remove whitespace, etc.)
        if self.device_token:
            self.device_token = self.device_token.strip()
        super().save(*args, **kwargs)