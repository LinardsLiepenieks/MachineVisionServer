import json
from typing import Any, Optional, Dict
import logging
from .codes import WebSocketCloseCodes

logger = logging.getLogger(__name__)


class WebSocketConnectionHandler:
    """Manages WebSocket connection operations and states."""

    @staticmethod
    async def accept(send: Any, subprotocols: Optional[list] = None) -> None:
        """Accepts a WebSocket connection with optional subprotocols."""
        message = {"type": "websocket.accept"}
        if subprotocols:
            message["subprotocol"] = subprotocols[0]
        await send(message)

    @staticmethod
    async def send_json_message(send: Any, **message_data) -> None:
        """Sends any JSON-serializable data through WebSocket."""
        await send(text_data=json.dumps(message_data))

    @staticmethod
    async def close(send: Any, code: WebSocketCloseCodes, reason: str) -> None:
        """
        Cleanly closes an already accepted WebSocket connection.
        """
        try:
            await send({"type": "websocket.close", "code": int(code), "reason": reason})
        except Exception as e:
            logger.error(f"Error closing WebSocket connection: {str(e)}")
            raise

    @staticmethod
    async def reject(send: Any, code: WebSocketCloseCodes, reason: str) -> None:
        """
        Rejects a connection by accepting first then closing with specific code.
        """
        try:
            await WebSocketConnectionHandler.accept(send)
            await WebSocketConnectionHandler.close(send, code, reason)
        except Exception as e:
            logger.error(f"Error rejecting WebSocket connection: {str(e)}")
            raise

    @staticmethod
    async def reject_unauthorized(send: Any) -> None:
        """Rejects unauthorized connection attempts."""
        await WebSocketConnectionHandler.reject(
            send, WebSocketCloseCodes.UNAUTHORIZED, "Unauthorized connection attempt"
        )

    @staticmethod
    async def reject_invalid_route(send: Any) -> None:
        """Rejects invalid route access attempts."""
        await WebSocketConnectionHandler.reject(
            send, WebSocketCloseCodes.INVALID_ROUTE, "Invalid route accessed"
        )

    @staticmethod
    async def reject_invalid_api_key(send: Any) -> None:
        """Rejects connections with invalid API keys."""
        await WebSocketConnectionHandler.reject(
            send, WebSocketCloseCodes.INVALID_API_KEY, "Invalid API key provided"
        )

    @staticmethod
    async def reject_malformed_api_key(send: Any) -> None:
        """Rejects connection due to malformed API key format."""
        await WebSocketConnectionHandler.reject(
            send,
            WebSocketCloseCodes.MALFORMED_API_KEY,
            "Malformed API key format",
        )
