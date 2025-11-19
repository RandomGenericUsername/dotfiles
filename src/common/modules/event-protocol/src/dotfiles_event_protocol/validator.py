"""Validation utilities for event protocol."""

from typing import Any

from pydantic import ValidationError

from .models import Message
from .types import MessageType


class MessageValidator:
    """Validator for event protocol messages."""

    @staticmethod
    def validate_message(data: dict[str, Any]) -> Message:
        """Validate and parse a message.
        
        Args:
            data: Raw message data
            
        Returns:
            Validated Message
            
        Raises:
            ValidationError: If message is invalid
        """
        return Message.from_dict(data)

    @staticmethod
    def validate_payload_type(message: Message, expected_type: MessageType) -> bool:
        """Validate that payload has expected type.
        
        Args:
            message: Message to validate
            expected_type: Expected message type
            
        Returns:
            True if payload type matches expected type
        """
        payload_type = message.payload.get("type")
        return payload_type == expected_type.value

    @staticmethod
    def is_valid_message(data: dict[str, Any]) -> bool:
        """Check if data is a valid message.
        
        Args:
            data: Raw message data
            
        Returns:
            True if valid, False otherwise
        """
        try:
            MessageValidator.validate_message(data)
            return True
        except ValidationError:
            return False

    @staticmethod
    def get_message_type(message: Message) -> MessageType | None:
        """Get message type from payload.
        
        Args:
            message: Message to inspect
            
        Returns:
            MessageType if found, None otherwise
        """
        payload_type = message.payload.get("type")
        if not payload_type:
            return None

        try:
            return MessageType(payload_type)
        except ValueError:
            return None

