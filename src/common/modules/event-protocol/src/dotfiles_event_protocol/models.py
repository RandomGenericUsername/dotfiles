"""Type-safe Pydantic models for event protocol."""

from datetime import datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from .types import MessageType, QueryType

# ============================================================================
# Base Message Model
# ============================================================================


class Message(BaseModel):
    """Base message structure for all events.

    All messages have this structure:
    - message_id: Unique identifier for the message
    - timestamp: ISO8601 timestamp when message was created
    - event_type: Event category (wallpaper, backup, etc.) - used for routing
    - payload: Generic dictionary containing message-specific data
    """

    message_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    event_type: str = Field(..., description="Event category for routing")
    payload: dict[str, Any] = Field(..., description="Message-specific data")

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate timestamp is ISO8601 format."""
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError as e:
            raise ValueError(f"Invalid ISO8601 timestamp: {v}") from e

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Message":
        """Create message from dictionary."""
        return cls.model_validate(data)


# ============================================================================
# Payload Models (Type-Safe Payloads)
# ============================================================================


class OperationStartedPayload(BaseModel):
    """Payload for operation_started message."""

    type: Literal[MessageType.OPERATION_STARTED] = (
        MessageType.OPERATION_STARTED
    )
    operation_id: str = Field(..., description="Unique operation identifier")
    operation_name: str = Field(..., description="Name of the operation")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Operation parameters"
    )


class OperationProgressPayload(BaseModel):
    """Payload for operation_progress message."""

    type: Literal[MessageType.OPERATION_PROGRESS] = (
        MessageType.OPERATION_PROGRESS
    )
    operation_id: str = Field(..., description="Unique operation identifier")
    step_id: str = Field(..., description="Current step identifier")
    step_name: str | None = Field(None, description="Human-readable step name")
    step_progress: float = Field(
        ..., ge=0.0, le=100.0, description="Step progress (0-100)"
    )
    overall_progress: float = Field(
        ..., ge=0.0, le=100.0, description="Overall progress (0-100)"
    )
    total_steps: int | None = Field(
        None, ge=1, description="Total number of steps"
    )
    current_step: int | None = Field(
        None, ge=1, description="Current step number"
    )


class OperationCompletedPayload(BaseModel):
    """Payload for operation_completed message."""

    type: Literal[MessageType.OPERATION_COMPLETED] = (
        MessageType.OPERATION_COMPLETED
    )
    operation_id: str = Field(..., description="Unique operation identifier")
    duration_seconds: float = Field(
        ..., ge=0.0, description="Operation duration in seconds"
    )
    result: dict[str, Any] = Field(
        default_factory=dict, description="Operation result data"
    )


class OperationFailedPayload(BaseModel):
    """Payload for operation_failed message."""

    type: Literal[MessageType.OPERATION_FAILED] = MessageType.OPERATION_FAILED
    operation_id: str = Field(..., description="Unique operation identifier")
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Human-readable error message")
    step_id: str | None = Field(None, description="Step where error occurred")
    traceback: str | None = Field(None, description="Optional traceback")


class StateUpdatePayload(BaseModel):
    """Payload for state_update message."""

    type: Literal[MessageType.STATE_UPDATE] = MessageType.STATE_UPDATE
    state_key: str = Field(
        ..., description="State key (e.g., 'current_wallpaper:DP-1')"
    )
    state_value: dict[str, Any] = Field(..., description="State value")


class QueryRequestPayload(BaseModel):
    """Payload for query_request message."""

    type: Literal[MessageType.QUERY_REQUEST] = MessageType.QUERY_REQUEST
    query_type: QueryType = Field(..., description="Type of query")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Query parameters"
    )


class QueryResponsePayload(BaseModel):
    """Payload for query_response message."""

    type: Literal[MessageType.QUERY_RESPONSE] = MessageType.QUERY_RESPONSE
    query_id: str = Field(..., description="ID of the query request")
    result: dict[str, Any] = Field(..., description="Query result")
    error: str | None = Field(
        None, description="Error message if query failed"
    )


# ============================================================================
# Typed Message Classes (Message + Typed Payload)
# ============================================================================


class OperationStartedMessage(BaseModel):
    """Type-safe message for operation_started."""

    message_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    event_type: str
    payload: OperationStartedPayload

    def to_generic(self) -> Message:
        """Convert to generic Message."""
        return Message(
            message_id=self.message_id,
            timestamp=self.timestamp,
            event_type=self.event_type,
            payload=self.payload.model_dump(),
        )


class OperationProgressMessage(BaseModel):
    """Type-safe message for operation_progress."""

    message_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    event_type: str
    payload: OperationProgressPayload

    def to_generic(self) -> Message:
        """Convert to generic Message."""
        return Message(
            message_id=self.message_id,
            timestamp=self.timestamp,
            event_type=self.event_type,
            payload=self.payload.model_dump(),
        )


class OperationCompletedMessage(BaseModel):
    """Type-safe message for operation_completed."""

    message_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    event_type: str
    payload: OperationCompletedPayload

    def to_generic(self) -> Message:
        """Convert to generic Message."""
        return Message(
            message_id=self.message_id,
            timestamp=self.timestamp,
            event_type=self.event_type,
            payload=self.payload.model_dump(),
        )


class OperationFailedMessage(BaseModel):
    """Type-safe message for operation_failed."""

    message_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    event_type: str
    payload: OperationFailedPayload

    def to_generic(self) -> Message:
        """Convert to generic Message."""
        return Message(
            message_id=self.message_id,
            timestamp=self.timestamp,
            event_type=self.event_type,
            payload=self.payload.model_dump(),
        )


class StateUpdateMessage(BaseModel):
    """Type-safe message for state_update."""

    message_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    event_type: str
    payload: StateUpdatePayload

    def to_generic(self) -> Message:
        """Convert to generic Message."""
        return Message(
            message_id=self.message_id,
            timestamp=self.timestamp,
            event_type=self.event_type,
            payload=self.payload.model_dump(),
        )


class QueryRequestMessage(BaseModel):
    """Type-safe message for query_request."""

    message_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    event_type: str
    payload: QueryRequestPayload

    def to_generic(self) -> Message:
        """Convert to generic Message."""
        return Message(
            message_id=self.message_id,
            timestamp=self.timestamp,
            event_type=self.event_type,
            payload=self.payload.model_dump(),
        )


class QueryResponseMessage(BaseModel):
    """Type-safe message for query_response."""

    message_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    event_type: str
    payload: QueryResponsePayload

    def to_generic(self) -> Message:
        """Convert to generic Message."""
        return Message(
            message_id=self.message_id,
            timestamp=self.timestamp,
            event_type=self.event_type,
            payload=self.payload.model_dump(),
        )
