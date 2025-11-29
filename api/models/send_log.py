from django.db import models
from django.utils import timezone
import uuid


class SendLog(models.Model):
    """
    Log of all notification sending attempts.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    app = models.ForeignKey('App', on_delete=models.CASCADE, related_name='send_logs')
    device = models.ForeignKey('Device', on_delete=models.CASCADE, related_name='send_logs')
    template = models.ForeignKey('Template', on_delete=models.SET_NULL, null=True, related_name='send_logs')
    notification_type = models.CharField(max_length=255)
    title = models.TextField()  # Rendered title
    body = models.TextField()   # Rendered body
    subject = models.TextField(blank=True)  # Rendered subject
    data = models.JSONField(default=dict, blank=True)  # Rendered data
    raw_request = models.JSONField()  # Original request data
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    provider_response = models.JSONField(default=dict, blank=True)  # Response from FCM/APNs
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'push_send_logs'
        verbose_name = 'Send Log'
        verbose_name_plural = 'Send Logs'
        indexes = [
            models.Index(fields=['app', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['device', 'created_at']),
        ]

    def __str__(self):
        return f"{self.app.name} - {self.notification_type} - {self.status}"