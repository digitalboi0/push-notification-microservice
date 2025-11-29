from rest_framework import serializers
from ..models import Template


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = [
            'id', 'app', 'name', 'title_template', 'body_template',
            'subject_template', 'data_template', 'is_active',
            'version', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'version', 'created_at', 'updated_at']

    def validate_name(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Template name cannot be empty")
        return value.strip()

    def validate_title_template(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Title template cannot be empty")
        return value.strip()

    def validate_body_template(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Body template cannot be empty")
        return value.strip()

    def create(self, validated_data):
        # Check if a template with the same name exists for this app
        existing_template = Template.objects.filter(
            app=validated_data['app'],
            name=validated_data['name']
        ).order_by('-version').first()
        
        if existing_template:
            validated_data['version'] = existing_template.version + 1
        else:
            validated_data['version'] = 1
            
        return super().create(validated_data)


class TemplatePreviewSerializer(serializers.Serializer):
    template_name = serializers.CharField(max_length=255)
    context = serializers.JSONField()