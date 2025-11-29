# api/utils/web_sender.py
import pywebpush
import json
import logging
from urllib.parse import urlparse
# DO NOT import settings from django.conf here for VAPID keys

logger = logging.getLogger(__name__)


def send_web_notification(device_token, title, body, data, vapid_public_key, vapid_private_key):
    """
    Send web push notification using Web Push protocol.
    subscription_info should contain endpoint, keys.p256dh, and keys.auth
    """
    # The keys are now passed in as arguments
    web_vapid_public_key = vapid_public_key
    web_vapid_private_key = vapid_private_key
    
    if not web_vapid_public_key or not web_vapid_private_key:
        return {
            'success': False,
            'error': 'Web VAPID keys not provided'
        }

    try:
        # Parse the device token (subscription info) from JSON string
        if isinstance(device_token, str):
            subscription_info = json.loads(device_token)
        else:
            subscription_info = device_token

        # Prepare the payload
        payload = {
            'title': title,
            'body': body,
        }
        
        if data:
            payload.update(data)

        # Extract the origin (scheme + host) from the subscription endpoint for the 'aud' claim
        endpoint_url = subscription_info.get('endpoint', '')
        parsed_url = urlparse(endpoint_url)
        audience = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # Send the notification - Use the correct function name: webpush
        response = pywebpush.webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=web_vapid_private_key,
            vapid_claims={
                "aud": audience, # Use the dynamically determined audience
                "exp": None,  # Expiration not set
                # Using a generic email for sub, consider making it configurable or app-specific
                "sub": "mailto:admin@example.com" 
            },
            timeout=30 # Increased timeout as suggested earlier
        )
        
        return {
            'success': True,
            'response': response.text,
            'status_code': response.status_code
        }
        
    except pywebpush.WebPushException as e:
        logger.error(f"Web push error: {str(e)}")
        
        # Check for specific error codes
        if e.response and e.response.status_code == 410:  # Subscription expired
            # Mark device as inactive - This requires the device ID, handled in the calling function
            # Device.objects.filter(device_token=subscription_info['endpoint']).update(is_active=False)
            logger.warning(f"Web push subscription expired for endpoint: {subscription_info.get('endpoint')}")
        
        return {
            'success': False,
            'error': str(e),
            'status_code': e.response.status_code if e.response else None
        }
    except Exception as e:
        logger.error(f"Web push send error: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }

# Keep other functions if any...