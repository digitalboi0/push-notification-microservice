from rest_framework import serializers
from ..models import App


class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = [
            'id', 'name', 'app_key', 'description', 'fcm_server_key',
            'apns_cert_path', 'apns_topic', 'web_vapid_public_key',
            'web_vapid_private_key', 'is_active', 'rate_limit', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'app_key', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Generate app key if not provided
        if 'app_key' not in validated_data or not validated_data['app_key']:
            import secrets
            validated_data['app_key'] = secrets.token_urlsafe(32)
        return super().create(validated_data)


class AppCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = [
            'name', 'description', 'fcm_server_key', 'apns_cert_path',
            'apns_topic', 'web_vapid_public_key', 'web_vapid_private_key',
            'rate_limit'
        ]

    def create(self, validated_data):
        import secrets
        validated_data['app_key'] = secrets.token_urlsafe(32)
        return App.objects.create(**validated_data)