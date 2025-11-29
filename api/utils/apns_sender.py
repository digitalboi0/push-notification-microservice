import jwt
import time
import json
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def send_apns_notification(device_token, title, body, data=None):
    """
    Send push notification via Apple Push Notification Service.
    """
    apns_cert_path = settings.APNS_CERT_PATH
    apns_topic = settings.APNS_TOPIC
    
    if not apns_cert_path or not apns_topic:
        return {
            'success': False,
            'error': 'APNs configuration not set'
        }

    # Prepare the payload
    apns_payload = {
        'aps': {
            'alert': {
                'title': title,
                'body': body
            },
            'badge': 1,
            'sound': 'default'
        }
    }
    
    if data:
        apns_payload.update(data)

    headers = {
        'apns-topic': apns_topic,
        'content-type': 'application/json'
    }

    try:
        # For APNs with certificate-based authentication
        response = requests.post(
            f'https://api.push.apple.com/3/device/{device_token}',
            headers=headers,
            data=json.dumps(apns_payload),
            cert=apns_cert_path,
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                'success': True,
                'response': response.text,
                'status_code': response.status_code
            }
        else:
            # Check for specific error codes
            error_msg = response.text
            if response.status_code == 410:  # Device token expired
                # Mark device as inactive
                from api.models import Device
                Device.objects.filter(device_token=device_token).update(is_active=False)
            
            return {
                'success': False,
                'error': f'APNs error: {error_msg}',
                'status_code': response.status_code
            }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"APNs request failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'status_code': getattr(e.response, 'status_code', None)
        }
    except Exception as e:
        logger.error(f"APNs send error: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


def send_apns_notification_with_auth_key(device_token, title, body, data=None):
    """
    Alternative method using JWT authentication for APNs.
    """
    # You would need to implement JWT token generation here
    # This requires your APNs auth key and team ID
    pass