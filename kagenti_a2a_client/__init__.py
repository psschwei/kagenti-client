"""Kagenti A2A Client - A Python client for interacting with Kagenti AI agents via A2A protocol."""

from .core.connection import A2AConnection, A2AConnectionError
from .core.session import SessionManager, Session, ConversationTurn
from .communication.sync_client import SyncClient, SyncClientError
from .models import (
    TaskResponse, TaskStatus, AgentCard, AgentCapability,
    JsonRpcResponse, JsonRpcError
)

__version__ = "0.1.0"
__all__ = [
    "A2AConnection", "A2AConnectionError",
    "SessionManager", "Session", "ConversationTurn", 
    "SyncClient", "SyncClientError",
    "TaskResponse", "TaskStatus", "AgentCard", "AgentCapability",
    "JsonRpcResponse", "JsonRpcError"
]