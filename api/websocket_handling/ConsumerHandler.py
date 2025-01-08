import json
from typing import Any, Optional, Dict
import logging
from .codes import WebSocketCloseCodes

logger = logging.getLogger(__name__)


class WebsocketConsumerHandler:
    """Manages WebSocket connection operations and states."""

    @staticmethod
    async def send_json_message(consumer, **message_data) -> None:
        """Sends any JSON-serializable data through WebSocket."""
        await consumer.send(text_data=json.dumps(message_data))

    @staticmethod
    async def approve_connection(consumer) -> None:
        """Accepts connection and sends success message."""
        await consumer.accept()
        await WebsocketConsumerHandler.send_json_message(
            consumer,
            type="auth_response",
            message=f"{consumer.auth_type} {consumer.auth_object} successfully connected",
            status="success",
        )

    @staticmethod
    async def close(consumer, code: WebSocketCloseCodes, reason: str) -> None:
        """
        Cleanly closes an already accepted WebSocket connection.
        """
        try:
            await consumer.close(code=int(code))
        except Exception as e:
            logger.error(f"Error closing WebSocket connection: {str(e)}")
            raise

    @staticmethod
    async def reject(consumer, code: WebSocketCloseCodes, reason: str) -> None:
        """
        Rejects a connection by accepting first then closing with specific code.

        Args:
            consumer: WebSocket consumer instance
            code: WebSocket close code from WebSocketCloseCodes enum
            reason: Explanation message for rejection
        """
        try:
            await consumer.accept()
            await consumer.close(code=int(code))
        except Exception as e:
            logger.error(f"Error rejecting WebSocket connection: {str(e)}")
            raise

    @staticmethod
    async def reject_unauthorized(consumer) -> None:
        """Rejects unauthorized connection attempts."""
        await WebsocketConsumerHandler.reject(
            consumer,
            WebSocketCloseCodes.UNAUTHORIZED,
            "Unauthorized connection attempt",
        )

    @staticmethod
    async def reject_invalid_route(consumer) -> None:
        """Rejects invalid route access attempts."""
        await WebsocketConsumerHandler.reject(
            consumer, WebSocketCloseCodes.INVALID_ROUTE, "Invalid route accessed"
        )

    @staticmethod
    async def reject_route_mismatch(consumer) -> None:
        """Rejects incorrect route access attempts (i.e. user accessing machine endpoint)."""
        await WebsocketConsumerHandler.reject(
            consumer,
            WebSocketCloseCodes.MISMATCH_FOR_ROUTE_AND_USER,
            "Invalid route accessed",
        )

    @staticmethod
    async def reject_invalid_api_key(consumer) -> None:
        """Rejects connections with invalid API keys."""
        await WebsocketConsumerHandler.reject(
            consumer, WebSocketCloseCodes.INVALID_API_KEY, "Invalid API key provided"
        )

    @staticmethod
    async def reject_malformed_api_key(consumer) -> None:
        """Rejects connection due to malformed API key format."""
        await WebsocketConsumerHandler.reject(
            consumer, WebSocketCloseCodes.MALFORMED_API_KEY, "Malformed API key format"
        )
