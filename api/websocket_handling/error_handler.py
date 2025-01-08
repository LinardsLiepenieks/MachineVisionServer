from enum import Enum
from typing import Optional
import logging


class ErrorCategory(Enum):
    """Categories of errors that can be safely communicated to clients"""

    CONNECTION_ERROR = "connection_error"
    AUTHENTICATION_ERROR = "authentication_error"
    VALIDATION_ERROR = "validation_error"
    PROCESSING_ERROR = "processing_error"
    RESOURCE_ERROR = "resource_error"


class ClientError:
    """Handles error messages that are safe to send to clients"""

    # Map internal errors to user-friendly messages
    ERROR_MESSAGES = {
        ConnectionError: (
            ErrorCategory.CONNECTION_ERROR,
            "Unable to establish connection. Please try again.",
        ),
        ValueError: (ErrorCategory.VALIDATION_ERROR, "Invalid input provided."),
        PermissionError: (
            ErrorCategory.AUTHENTICATION_ERROR,
            "You don't have permission to perform this action.",
        ),
        ResourceWarning: (
            ErrorCategory.RESOURCE_ERROR,
            "The requested resource is currently unavailable.",
        ),
    }

    @staticmethod
    def handle_error(error: Exception, logger: logging.Logger) -> dict:
        """
        Converts internal errors to client-safe messages while logging the full error details

        Args:
            error: The caught exception
            logger: Logger instance for recording full error details

        Returns:
            Dict containing safe error message for client
        """
        # Log the full error for debugging
        logger.error(f"Internal error: {str(error)}", exc_info=True)

        # Get the appropriate error category and message
        error_category, message = ClientError.ERROR_MESSAGES.get(
            type(error),
            (
                ErrorCategory.PROCESSING_ERROR,
                "An unexpected error occurred. Please try again later.",
            ),
        )

        return {
            "type": "error",
            "category": error_category.value,
            "message": message,
            "code": hash(str(error)) % 1000000,  # Generate a traceable error code
        }
