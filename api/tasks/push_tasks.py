# api/tasks/push_tasks.py
from celery import shared_task
import logging
import requests
import json
from django.utils import timezone
from ..models import SendLog, Device # Import Device if needed to check/update status, though SendLog has device_id
from ..utils.fcm_sender import send_fcm_notification
from ..utils.apns_sender import send_apns_notification
from ..utils.web_sender import send_web_notification

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_push_notification_task(
    self, send_log_id, device_token, platform, title, body, data, subject=None
):
    """
    Celery task to send push notification via FCM, APNs, or web push.
    """
    try:
        send_log = SendLog.objects.get(id=send_log_id)
        
        # Get the App instance from the SendLog (via Device or Template)
        # Assuming SendLog.device.app is the correct path
        app = send_log.device.app
        
        # Update status to processing
        send_log.status = 'pending'
        send_log.sent_at = timezone.now()
        send_log.save(update_fields=['status', 'sent_at'])

        if platform == 'android':
            # Send via FCM - Uses keys from App model
            response = send_fcm_notification(
                device_token=device_token,
                title=title,
                body=body,
                data=data
            )
        elif platform == 'ios':
            # Send via APNs - Uses keys from App model
            response = send_apns_notification(
                device_token=device_token,
                title=title,
                body=body,
                data=data
            )
        elif platform == 'web':
            # Send via Web Push - Uses keys from App model
            # Pass the keys from the App instance to the sender function
            response = send_web_notification(
                device_token=device_token,
                title=title,
                body=body,
                data=data,
                vapid_public_key=app.web_vapid_public_key, # Get from App model
                vapid_private_key=app.web_vapid_private_key # Get from App model
            )
        else:
            raise ValueError(f"Unsupported platform: {platform}")

        # Update send log with response
        send_log.provider_response = response
        send_log.status = 'sent' if response.get('success') else 'failed'
        send_log.error_message = response.get('error', '')
        send_log.save(update_fields=['provider_response', 'status', 'error_message', 'updated_at'])

        logger.info(f"Notification sent successfully to {platform} device. Response: {response}")
        return response

    except SendLog.DoesNotExist:
        logger.error(f"SendLog with id {send_log_id} does not exist")
        return {'success': False, 'error': 'SendLog not found'}
    
    except Exception as exc:
        logger.error(f"Error sending notification: {str(exc)}", exc_info=True)
        
        # Update send log with error
        try:
            send_log = SendLog.objects.get(id=send_log_id)
            send_log.status = 'failed'
            send_log.error_message = str(exc)
            send_log.save(update_fields=['status', 'error_message', 'updated_at'])
        except SendLog.DoesNotExist:
            pass
        
        # Retry the task
        raise self.retry(exc=exc, countdown=60)  # Retry after 1 minute


# ... other tasks ...