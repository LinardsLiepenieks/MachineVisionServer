from enum import IntEnum


class WebSocketCloseCodes(IntEnum):
    """Explicit enumeration of WebSocket close codes for the application."""

    INVALID_ROUTE = 4001
    INVALID_API_KEY = 4002
    MISMATCH_FOR_ROUTE_AND_USER = 4003
    MALFORMED_API_KEY = 4004
    INTERNAL_ERROR = 4500
