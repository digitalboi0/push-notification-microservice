from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
import logging
from ..models import Device, Template, SendLog
from ..serializers import NotificationRequestSerializer, BulkNotificationRequestSerializer
from ..tasks.push_tasks import send_push_notification_task
from ..utils.template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)




class SendNotificationView(APIView):
    """
    API view to send push notifications.
    """
    
    def post(self, request):
        serializer = NotificationRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors,
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        
        try:
            with transaction.atomic():
                # Get or create device based on app, user_identifier, and platform
                # Use a more specific user_identifier if possible, falling back to email or name
                user_identifier = validated_data['user'].get('id') or validated_data['user'].get('email') or validated_data['user'].get('name') or 'unknown'
                
                device, created = Device.objects.get_or_create(
                    app=request.app,
                    user_identifier=user_identifier,
                    platform=validated_data['platform'],
                    defaults={
                        'device_token': validated_data['device_token'],
                        'is_active': True
                    }
                )
                
                # If the device existed but the token is different, update it
                if not created and device.device_token != validated_data['device_token']:
                    logger.info(f"Updating device token for {device.app.name} - {device.platform} - {device.user_identifier}")
                    device.device_token = validated_data['device_token']
                    device.is_active = True # Reset active status if token is updated
                    device.push_token_updated_at = timezone.now()
                    device.save(update_fields=['device_token', 'is_active', 'push_token_updated_at'])
                
                if not device.is_active:
                    return Response({
                        'success': False,
                        'message': 'Device is not active',
                        'data': None
                    }, status=status.HTTP_400_BAD_REQUEST)

                # If title and body are provided, use them directly
                if validated_data.get('title') and validated_data.get('body'):
                    title = validated_data['title']
                    body = validated_data['body']
                    subject = validated_data.get('subject', '')
                    data = validated_data.get('data', {})
                else:
                    # Render template
                    template = Template.objects.filter(
                        app=request.app,
                        name=validated_data['notification_type'],
                        is_active=True
                    ).order_by('-version').first()
                    
                    if not template:
                        return Response({
                            'success': False,
                            'message': f'Template "{validated_data["notification_type"]}" not found',
                            'data': None
                        }, status=status.HTTP_404_NOT_FOUND)

                    renderer = TemplateRenderer(template)
                    rendered_title = renderer.render_title(validated_data['user'])
                    rendered_body = renderer.render_body(validated_data['user'])
                    rendered_subject = renderer.render_subject(validated_data['user'])
                    rendered_data = renderer.render_data(validated_data['user'], validated_data['data'])

                    title = rendered_title
                    body = rendered_body
                    subject = rendered_subject
                    data = rendered_data

                # Create send log
                send_log = SendLog.objects.create(
                    app=request.app,
                    device=device,
                    template=template if not created else None,
                    notification_type=validated_data['notification_type'],
                    title=title,
                    body=body,
                    subject=subject,
                    data=data,
                    raw_request=validated_data,
                    status='pending'
                )

            # Send notification asynchronously
            try:
                send_push_notification_task.delay(
                    send_log_id=str(send_log.id),
                    device_token=device.device_token, # Use the potentially updated token
                    platform=validated_data['platform'],
                    title=title,
                    body=body,
                    data=data,
                    subject=subject
                )
                message = 'Notification queued for sending'
                status_code = status.HTTP_202_ACCEPTED
            except Exception as e:
                # If Celery is unavailable, mark the log as failed and return an error
                logger.error(f"Error queuing notification with Celery: {str(e)}", exc_info=True)
                send_log.status = 'failed'
                send_log.error_message = f"Celery error: {str(e)}"
                send_log.save(update_fields=['status', 'error_message', 'updated_at'])
                return Response({
                    'success': False,
                    'message': 'Failed to queue notification (Celery unavailable)',
                    'data': None
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            return Response({
                'success': True,
                'message': message,
                'data': {
                    'send_log_id': str(send_log.id),
                    'device_id': str(device.id)
                }
            }, status=status_code)

        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}", exc_info=True)
            # Use the correct status code constant
            return Response({
                'success': False,
                'message': 'Internal server error',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) # Fixed the status code




# Keep the BulkSendNotificationView similar, applying the same Celery error handling
class BulkSendNotificationView(APIView):
    """
    API view to send multiple push notifications in bulk.
    """
    
    def post(self, request):
        serializer = BulkNotificationRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors,
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        notifications = request.data.get('notifications', [])
        results = []
        
        for notification_data in notifications:
            # Validate each notification
            single_serializer = NotificationRequestSerializer(data=notification_data)
            if not single_serializer.is_valid():
                results.append({
                    'success': False,
                    'message': 'Invalid notification data',
                    'errors': single_serializer.errors
                })
                continue

            validated_data = single_serializer.validated_data
            
            try:
                with transaction.atomic():
                    # Get or create device
                    device, created = Device.objects.get_or_create(
                        app=request.app, # This comes from your middleware
                        device_token=validated_data['device_token'],
                        defaults={
                            'platform': validated_data['platform'],
                            'user_identifier': validated_data['user'].get('id', 'unknown'),
                            'is_active': True
                        }
                    )
                    
                    if not device.is_active:
                        results.append({
                            'success': False,
                            'message': 'Device is not active'
                        })
                        continue

                    # Render template or use provided title/body
                    if validated_data.get('title') and validated_data.get('body'):
                        title = validated_data['title']
                        body = validated_data['body']
                        subject = validated_data.get('subject', '')
                        data = validated_data.get('data', {})
                    else:
                        template = Template.objects.filter(
                            app=request.app,
                            name=validated_data['notification_type'],
                            is_active=True
                        ).order_by('-version').first()
                        
                        if not template:
                            results.append({
                                'success': False,
                                'message': f'Template "{validated_data["notification_type"]}" not found'
                            })
                            continue

                        renderer = TemplateRenderer(template)
                        rendered_title = renderer.render_title(validated_data['user'])
                        rendered_body = renderer.render_body(validated_data['user'])
                        rendered_subject = renderer.render_subject(validated_data['user'])
                        rendered_data = renderer.render_data(validated_data['user'], validated_data['data'])

                        title = rendered_title
                        body = rendered_body
                        subject = rendered_subject
                        data = rendered_data

                    # Create send log
                    send_log = SendLog.objects.create(
                        app=request.app,
                        device=device,
                        template=template if not created else None,
                        notification_type=validated_data['notification_type'],
                        title=title,
                        body=body,
                        subject=subject,
                        data=data,
                        raw_request=validated_data,
                        status='pending'
                    )

                    # Send notification asynchronously - wrap in try-catch for Celery issues
                    try:
                        send_push_notification_task.delay(
                            send_log_id=str(send_log.id),
                            device_token=validated_data['device_token'],
                            platform=validated_data['platform'],
                            title=title,
                            body=body,
                            data=data,
                            subject=subject
                        )
                        results.append({
                            'success': True,
                            'message': 'Notification queued for sending',
                            'data': {
                                'send_log_id': str(send_log.id),
                                'device_id': str(device.id)
                            }
                        })
                    except Exception as e:
                        logger.error(f"Error queuing notification with Celery: {str(e)}", exc_info=True)
                        # Update the log to show it failed to queue
                        send_log.status = 'failed'
                        send_log.error_message = f"Celery error: {str(e)}"
                        send_log.save(update_fields=['status', 'error_message', 'updated_at'])
                        results.append({
                            'success': False,
                            'message': 'Failed to queue notification (Celery unavailable)'
                        })

            except Exception as e:
                logger.error(f"Error sending bulk notification: {str(e)}", exc_info=True)
                results.append({
                    'success': False,
                    'message': 'Internal server error'
                })

        # Determine overall success based on individual results
        overall_success = any(result['success'] for result in results)
        overall_status = status.HTTP_202_ACCEPTED if overall_success else status.HTTP_500_INTERNAL_ERROR

        return Response({
            'success': overall_success,
            'message': f'Processed {len(results)} notifications',
            'data': {
                'results': results,
                'total_processed': len(results)
            }
        }, status=overall_status)