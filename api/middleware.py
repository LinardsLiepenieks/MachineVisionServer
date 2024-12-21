from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist, ValidationError
import logging
from typing import Dict, Any
from .models import ApiKey
from .websocket_handling.handler import WebSocketConnectionHandler

logger = logging.getLogger(__name__)


class ApiKeyValidationMiddleware(BaseMiddleware):
    async def __call__(self, scope: Dict[str, Any], receive: Any, send: Any) -> Any:
        try:
            headers = dict(scope["headers"])
            authorization_header = self._extract_header(
                headers, "sec-websocket-protocol"
            )
            api_key = self._extract_api_key(authorization_header)

            if not api_key:
                await WebSocketConnectionHandler.reject_invalid_api_key(send)
                return

            auth_result = await self._validate_api_key(api_key, send)
            if not auth_result:
                return

            scope["auth_type"] = auth_result["type"]
            scope["auth_object"] = auth_result["object"]
            return await super().__call__(scope, receive, send)

        except Exception as e:
            logger.error(f"API key validation error: {str(e)}")
            await WebSocketConnectionHandler.reject_invalid_api_key(send)
            return

    def _extract_header(self, headers: dict, header_name: str) -> str:
        return headers.get(header_name.encode(), b"").decode("utf-8")

    def _extract_api_key(self, header: str) -> str:
        if not header:
            return None

        # Split header into parts and validate format
        parts = header.strip().split()

        # Check if it's a Bearer token
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]
        # Check if it's a single token (backwards compatibility)
        if len(parts) == 1 and parts[0]:
            return parts[0]

        return None

    async def _validate_api_key(self, api_key: str, send: Any) -> Dict[str, Any] | None:
        """Validate the API key and handle validation errors."""
        try:
            auth_result = await self._find_api_key(api_key)
            if auth_result["type"] == "error":
                await WebSocketConnectionHandler.reject_invalid_api_key(send)
                return None
            return auth_result

        except ValidationError:
            await WebSocketConnectionHandler.reject_malformed_api_key(send)
            return None

    @database_sync_to_async
    def _find_api_key(self, key: str) -> Dict[str, Any]:
        """Finds and validates an API key across all APIKey subclasses."""
        try:
            for model in ApiKey.get_all_subclasses():
                try:
                    api_key = model.objects.get(key=key, is_active=True)
                    return api_key.get_auth_object()
                except ObjectDoesNotExist:
                    continue
            return {"type": "error", "object": None}
        except ValidationError:
            # Re-raise the ValidationError to be caught in __call__
            raise


class InvalidRouteErrorMiddleware(BaseMiddleware):
    """Middleware that handles websocket routing errors by sending a custom close code 4001 when an invalid route is accessed."""

    async def __call__(self, scope, receive, send):
        try:
            await super().__call__(scope, receive, send)
        except ValueError as e:
            if "No route found" in str(e):
                await WebSocketConnectionHandler.reject_invalid_route(send)
                logger.error(f"Unexpected ValueError: {str(e)}")
                raise e
