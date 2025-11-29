from rest_framework import serializers
from ..models import Device


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            'id', 'app', 'device_token', 'platform', 'user_identifier',
            'is_active', 'push_token_updated_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'push_token_updated_at']

    def validate_device_token(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Device token cannot be empty")
        return value.strip()

    def validate(self, attrs):
        # Check if device already exists for this user and platform
        app = attrs.get('app')
        user_identifier = attrs.get('user_identifier')
        platform = attrs.get('platform')
        
        if Device.objects.filter(
            app=app, 
            user_identifier=user_identifier, 
            platform=platform
        ).exists():
            raise serializers.ValidationError(
                "Device already exists for this user and platform combination"
            )
        return attrs


class DeviceRegistrationSerializer(serializers.Serializer):
    device_token = serializers.CharField()
    platform = serializers.ChoiceField(choices=['ios', 'android', 'web'])
    user_identifier = serializers.CharField(max_length=255)