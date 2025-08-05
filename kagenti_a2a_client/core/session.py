"""Session management for multi-turn conversations with A2A agents."""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class ConversationTurn:
    """Represents a single turn in a conversation."""
    
    turn_id: str
    input_text: str
    output_text: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class Session:
    """Represents a conversation session with an agent."""
    
    session_id: str
    agent_url: str
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    turns: List[ConversationTurn] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    
    def add_turn(
        self,
        input_text: str,
        output_text: Optional[str] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationTurn:
        """Add a new turn to the conversation.
        
        Args:
            input_text: User input text
            output_text: Agent response text
            error: Error message if the turn failed
            metadata: Additional metadata for the turn
            
        Returns:
            The created ConversationTurn
        """
        turn = ConversationTurn(
            turn_id=str(uuid.uuid4()),
            input_text=input_text,
            output_text=output_text,
            error=error,
            metadata=metadata or {}
        )
        
        self.turns.append(turn)
        self.last_activity = datetime.now()
        return turn
    
    def get_conversation_history(self, max_turns: Optional[int] = None) -> List[ConversationTurn]:
        """Get conversation history.
        
        Args:
            max_turns: Maximum number of recent turns to return
            
        Returns:
            List of conversation turns
        """
        if max_turns is None:
            return self.turns.copy()
        return self.turns[-max_turns:] if self.turns else []
    
    def is_expired(self, timeout_minutes: int = 60) -> bool:
        """Check if the session has expired.
        
        Args:
            timeout_minutes: Session timeout in minutes
            
        Returns:
            True if the session has expired
        """
        timeout_delta = timedelta(minutes=timeout_minutes)
        return datetime.now() - self.last_activity > timeout_delta


class SessionManager:
    """Manages conversation sessions with A2A agents."""
    
    def __init__(self, default_timeout_minutes: int = 60):
        """Initialize session manager.
        
        Args:
            default_timeout_minutes: Default session timeout in minutes
        """
        self._sessions: Dict[str, Session] = {}
        self._lock = Lock()
        self.default_timeout = default_timeout_minutes
    
    def create_session(
        self,
        agent_url: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Session:
        """Create a new conversation session.
        
        Args:
            agent_url: URL of the target agent
            session_id: Custom session ID (auto-generated if not provided)
            metadata: Initial session metadata
            
        Returns:
            Created Session object
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        with self._lock:
            if session_id in self._sessions:
                raise ValueError(f"Session {session_id} already exists")
            
            session = Session(
                session_id=session_id,
                agent_url=agent_url,
                metadata=metadata or {}
            )
            
            self._sessions[session_id] = session
            return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get an existing session.
        
        Args:
            session_id: Session ID to retrieve
            
        Returns:
            Session object if found, None otherwise
        """
        with self._lock:
            return self._sessions.get(session_id)
    
    def get_or_create_session(
        self,
        session_id: str,
        agent_url: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Session:
        """Get existing session or create a new one.
        
        Args:
            session_id: Session ID
            agent_url: URL of the target agent
            metadata: Session metadata (used only if creating new session)
            
        Returns:
            Session object
        """
        session = self.get_session(session_id)
        if session is None:
            session = self.create_session(agent_url, session_id, metadata)
        else:
            # Update last activity
            session.last_activity = datetime.now()
        return session
    
    def close_session(self, session_id: str) -> bool:
        """Close and remove a session.
        
        Args:
            session_id: Session ID to close
            
        Returns:
            True if session was found and closed, False otherwise
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.is_active = False
                del self._sessions[session_id]
                return True
            return False
    
    def cleanup_expired_sessions(self, timeout_minutes: Optional[int] = None) -> List[str]:
        """Remove expired sessions.
        
        Args:
            timeout_minutes: Custom timeout (uses default if not provided)
            
        Returns:
            List of session IDs that were cleaned up
        """
        timeout = timeout_minutes or self.default_timeout
        expired_sessions = []
        
        with self._lock:
            for session_id, session in list(self._sessions.items()):
                if session.is_expired(timeout):
                    session.is_active = False
                    del self._sessions[session_id]
                    expired_sessions.append(session_id)
        
        return expired_sessions
    
    def list_active_sessions(self) -> List[str]:
        """Get list of active session IDs.
        
        Returns:
            List of active session IDs
        """
        with self._lock:
            return [
                session_id for session_id, session in self._sessions.items()
                if session.is_active
            ]
    
    def get_session_count(self) -> int:
        """Get the number of active sessions.
        
        Returns:
            Number of active sessions
        """
        with self._lock:
            return len([s for s in self._sessions.values() if s.is_active])
    
    def clear_all_sessions(self) -> int:
        """Clear all sessions.
        
        Returns:
            Number of sessions that were cleared
        """
        with self._lock:
            count = len(self._sessions)
            for session in self._sessions.values():
                session.is_active = False
            self._sessions.clear()
            return count