import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def send_fcm_notification(device_token, title, body, data=None):
    """
    Send push notification via Firebase Cloud Messaging.
    """
    fcm_server_key = settings.FCM_SERVER_KEY
    
    if not fcm_server_key:
        return {
            'success': False,
            'error': 'FCM server key not configured'
        }

    headers = {
        'Authorization': f'key={fcm_server_key}',
        'Content-Type': 'application/json'
    }

    payload = {
        'to': device_token,
        'notification': {
            'title': title,
            'body': body
        },
        'data': data or {}
    }

    try:
        response = requests.post(
            'https://fcm.googleapis.com/fcm/send',
            headers=headers,
            data=json.dumps(payload),
            timeout=10
        )
        
        response.raise_for_status()
        
        result = response.json()
        
        # Check if the token is invalid
        if result.get('results') and result['results'][0].get('error') == 'InvalidRegistration':
            # Mark device as inactive
            from api.models import Device
            Device.objects.filter(device_token=device_token).update(is_active=False)
        
        return {
            'success': True,
            'response': result,
            'status_code': response.status_code
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"FCM request failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'status_code': getattr(e.response, 'status_code', None)
        }
    except Exception as e:
        logger.error(f"FCM send error: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


def send_fcm_notification_batch(device_tokens, title, body, data=None):
    """
    Send push notification to multiple devices via FCM (batch).
    """
    fcm_server_key = settings.FCM_SERVER_KEY
    
    if not fcm_server_key:
        return {
            'success': False,
            'error': 'FCM server key not configured'
        }

    headers = {
        'Authorization': f'key={fcm_server_key}',
        'Content-Type': 'application/json'
    }

    payload = {
        'registration_ids': device_tokens,
        'notification': {
            'title': title,
            'body': body
        },
        'data': data or {}
    }

    try:
        response = requests.post(
            'https://fcm.googleapis.com/fcm/send',
            headers=headers,
            data=json.dumps(payload),
            timeout=10
        )
        
        response.raise_for_status()
        
        result = response.json()
        
        # Handle invalid tokens
        if result.get('results'):
            for i, result_item in enumerate(result['results']):
                if result_item.get('error') == 'InvalidRegistration':
                    invalid_token = device_tokens[i]
                    from api.models import Device
                    Device.objects.filter(device_token=invalid_token).update(is_active=False)
        
        return {
            'success': True,
            'response': result,
            'status_code': response.status_code
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"FCM batch request failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'status_code': getattr(e.response, 'status_code', None)
        }
    except Exception as e:
        logger.error(f"FCM batch send error: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }