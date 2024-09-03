from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user_or_machine_from_api_key(api_key: str) -> Dict[str, Any]:
    from .models import APIKey, MachineApiKey

    api_key_models = [APIKey, MachineApiKey]

    for model in api_key_models:
        try:
            api_key_obj = model.objects.get(key=api_key, is_active=True)
            
            if isinstance(api_key_obj, APIKey):
                logger.info("Valid user API key used")
                return {'type': 'user', 'object': api_key_obj.profile.user}
            elif isinstance(api_key_obj, MachineApiKey):
                logger.info("Valid machine API key used")
                return {'type': 'machine', 'object': api_key_obj.machine}
        except ObjectDoesNotExist:
            continue
    
    logger.warning(f"Invalid API key used: {api_key}")
    return {'type': 'anonymous', 'object': AnonymousUser()}

class APIWSKeyAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope: Dict[str, Any], receive: Any, send: Any) -> Any:
        headers = dict(scope['headers'])
        authorization = headers.get(b'sec-websocket-protocol', b'').decode('utf-8')

        api_key = authorization.split(' ')[-1] if authorization.startswith('Bearer ') else authorization

        if api_key:
            auth_result = await get_user_or_machine_from_api_key(api_key)
        else:
            logger.warning("No API key found in headers")
            auth_result = {'type': 'anonymous', 'object': AnonymousUser()}

        scope['auth_type'] = auth_result['type']
        scope['auth_object'] = auth_result['object']
                
        return await super().__call__(scope, receive, send)