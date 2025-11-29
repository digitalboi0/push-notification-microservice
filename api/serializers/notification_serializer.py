from rest_framework import serializers
from ..models import Device, Template
from ..utils.template_renderer import validate_template_context


class NotificationRequestSerializer(serializers.Serializer):
    notification_type = serializers.CharField(max_length=255)
    device_token = serializers.CharField()
    platform = serializers.ChoiceField(choices=['ios', 'android', 'web'])
    user = serializers.JSONField()
    data = serializers.JSONField(default=dict)
    title = serializers.CharField(required=False, allow_blank=True, max_length=255)
    body = serializers.CharField(required=False, allow_blank=True)

    def validate_device_token(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Device token cannot be empty")
        return value.strip()

    def validate_user(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("User must be a JSON object")
        if not value:
            raise serializers.ValidationError("User object cannot be empty")
        return value

    def validate_data(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Data must be a JSON object")
        return value

    def validate(self, attrs):
        # If title and body are provided, they override template rendering
        if attrs.get('title') or attrs.get('body'):
            if not attrs.get('title'):
                raise serializers.ValidationError("Title is required when body is provided")
            if not attrs.get('body'):
                raise serializers.ValidationError("Body is required when title is provided")
        return attrs


class BulkNotificationRequestSerializer(serializers.Serializer):
    notifications = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=100
    )