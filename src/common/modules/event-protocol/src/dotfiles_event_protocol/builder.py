"""Message builder utilities for creating type-safe messages."""

from typing import Any

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
from .types import QueryType


class MessageBuilder:
    """Builder for creating type-safe messages."""

    @staticmethod
    def operation_started(
        event_type: str,
        operation_id: str,
        operation_name: str,
        parameters: dict[str, Any] | None = None,
    ) -> Message:
        """Create operation_started message.

        Args:
            event_type: Event category (e.g., "wallpaper", "backup")
            operation_id: Unique operation identifier
            operation_name: Name of the operation
            parameters: Optional operation parameters

        Returns:
            Type-safe Message
        """
        msg = OperationStartedMessage(
            event_type=event_type,
            payload=OperationStartedPayload(
                operation_id=operation_id,
                operation_name=operation_name,
                parameters=parameters or {},
            ),
        )
        return msg.to_generic()

    @staticmethod
    def operation_progress(
        event_type: str,
        operation_id: str,
        step_id: str,
        step_progress: float,
        overall_progress: float,
        step_name: str | None = None,
        total_steps: int | None = None,
        current_step: int | None = None,
    ) -> Message:
        """Create operation_progress message.

        Args:
            event_type: Event category
            operation_id: Unique operation identifier
            step_id: Current step identifier
            step_progress: Step progress (0-100)
            overall_progress: Overall progress (0-100)
            step_name: Optional human-readable step name
            total_steps: Optional total number of steps
            current_step: Optional current step number

        Returns:
            Type-safe Message
        """
        msg = OperationProgressMessage(
            event_type=event_type,
            payload=OperationProgressPayload(
                operation_id=operation_id,
                step_id=step_id,
                step_progress=step_progress,
                overall_progress=overall_progress,
                step_name=step_name,
                total_steps=total_steps,
                current_step=current_step,
            ),
        )
        return msg.to_generic()

    @staticmethod
    def operation_completed(
        event_type: str,
        operation_id: str,
        duration_seconds: float,
        result: dict[str, Any] | None = None,
    ) -> Message:
        """Create operation_completed message.

        Args:
            event_type: Event category
            operation_id: Unique operation identifier
            duration_seconds: Operation duration in seconds
            result: Optional operation result data

        Returns:
            Type-safe Message
        """
        msg = OperationCompletedMessage(
            event_type=event_type,
            payload=OperationCompletedPayload(
                operation_id=operation_id,
                duration_seconds=duration_seconds,
                result=result or {},
            ),
        )
        return msg.to_generic()

    @staticmethod
    def operation_failed(
        event_type: str,
        operation_id: str,
        error_code: str,
        error_message: str,
        step_id: str | None = None,
        traceback: str | None = None,
    ) -> Message:
        """Create operation_failed message.

        Args:
            event_type: Event category
            operation_id: Unique operation identifier
            error_code: Error code
            error_message: Human-readable error message
            step_id: Optional step where error occurred
            traceback: Optional traceback

        Returns:
            Type-safe Message
        """
        msg = OperationFailedMessage(
            event_type=event_type,
            payload=OperationFailedPayload(
                operation_id=operation_id,
                error_code=error_code,
                error_message=error_message,
                step_id=step_id,
                traceback=traceback,
            ),
        )
        return msg.to_generic()

    @staticmethod
    def state_update(
        event_type: str,
        state_key: str,
        state_value: dict[str, Any],
    ) -> Message:
        """Create state_update message.

        Args:
            event_type: Event category
            state_key: State key (e.g., "current_wallpaper:DP-1")
            state_value: State value

        Returns:
            Type-safe Message
        """
        msg = StateUpdateMessage(
            event_type=event_type,
            payload=StateUpdatePayload(
                state_key=state_key,
                state_value=state_value,
            ),
        )
        return msg.to_generic()

    @staticmethod
    def query_request(
        event_type: str,
        query_type: QueryType,
        parameters: dict[str, Any] | None = None,
    ) -> Message:
        """Create query_request message.

        Args:
            event_type: Event category
            query_type: Type of query
            parameters: Optional query parameters

        Returns:
            Type-safe Message
        """
        msg = QueryRequestMessage(
            event_type=event_type,
            payload=QueryRequestPayload(
                query_type=query_type,
                parameters=parameters or {},
            ),
        )
        return msg.to_generic()

    @staticmethod
    def query_response(
        event_type: str,
        query_id: str,
        result: dict[str, Any],
        error: str | None = None,
    ) -> Message:
        """Create query_response message.

        Args:
            event_type: Event category
            query_id: ID of the query request
            result: Query result
            error: Optional error message

        Returns:
            Type-safe Message
        """
        msg = QueryResponseMessage(
            event_type=event_type,
            payload=QueryResponsePayload(
                query_id=query_id,
                result=result,
                error=error,
            ),
        )
        return msg.to_generic()
