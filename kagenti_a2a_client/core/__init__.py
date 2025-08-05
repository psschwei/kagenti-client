"""Core components for A2A client."""

from .connection import A2AConnection, A2AConnectionError
from .session import SessionManager, Session, ConversationTurn

__all__ = [
    "A2AConnection", "A2AConnectionError",
    "SessionManager", "Session", "ConversationTurn"
]