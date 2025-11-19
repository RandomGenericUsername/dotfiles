"""Type-safe event protocol for dotfiles event system.

This module provides type-safe Pydantic models for the event protocol used
between dotfiles-manager, dotfiles-daemon, and monitoring clients.

Example usage:

    # Create a message using the builder
    from dotfiles_event_protocol import MessageBuilder
    
    message = MessageBuilder.operation_progress(
        event_type="wallpaper",
        operation_id="uuid-1234",
        step_id="generate_effects",
        step_progress=50.0,
        overall_progress=50.0,
    )
    
    # Validate a message
    from dotfiles_event_protocol import MessageValidator
    
    is_valid = MessageValidator.is_valid_message(message.to_dict())
    
    # Use typed models directly
    from dotfiles_event_protocol import (
        Message,
        OperationProgressPayload,
        OperationProgressMessage,
    )
    
    payload = OperationProgressPayload(
        operation_id="uuid-1234",
        step_id="generate_effects",
        step_progress=50.0,
        overall_progress=50.0,
    )
    
    msg = OperationProgressMessage(
        event_type="wallpaper",
        payload=payload,
    )
"""

from .builder import MessageBuilder
from .models import (
    Message,
    OperationCompletedMessage,
    OperationCompletedPayload,
    OperationFailedMessage,
    OperationFailedPayload,
    OperationProgressMessage,
    OperationProgressPayload,
    OperationStartedMessage,
    OperationStartedPayload,
    QueryRequestMessage,
    QueryRequestPayload,
    QueryResponseMessage,
    QueryResponsePayload,
    StateUpdateMessage,
    StateUpdatePayload,
)
from .types import MessageType, QueryType
from .validator import MessageValidator

__all__ = [
    # Builder
    "MessageBuilder",
    # Validator
    "MessageValidator",
    # Base models
    "Message",
    # Payload models
    "OperationStartedPayload",
    "OperationProgressPayload",
    "OperationCompletedPayload",
    "OperationFailedPayload",
    "StateUpdatePayload",
    "QueryRequestPayload",
    "QueryResponsePayload",
    # Typed message models
    "OperationStartedMessage",
    "OperationProgressMessage",
    "OperationCompletedMessage",
    "OperationFailedMessage",
    "StateUpdateMessage",
    "QueryRequestMessage",
    "QueryResponseMessage",
    # Enums
    "MessageType",
    "QueryType",
]

