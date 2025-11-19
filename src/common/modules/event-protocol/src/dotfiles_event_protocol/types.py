"""Type aliases and enums for event protocol."""

from enum import Enum


class MessageType(str, Enum):
    """Message types for event protocol."""

    OPERATION_STARTED = "operation_started"
    OPERATION_PROGRESS = "operation_progress"
    OPERATION_COMPLETED = "operation_completed"
    OPERATION_FAILED = "operation_failed"
    STATE_UPDATE = "state_update"
    QUERY_REQUEST = "query_request"
    QUERY_RESPONSE = "query_response"


class QueryType(str, Enum):
    """Query types for daemon queries."""

    GET_CURRENT_STATE = "get_current_state"
    GET_OPERATION_STATUS = "get_operation_status"
    LIST_EVENT_TYPES = "list_event_types"
    GET_EVENT_HISTORY = "get_event_history"

