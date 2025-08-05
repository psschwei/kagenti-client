"""Synchronous client for A2A agent communication."""

from typing import Optional, Dict, Any
import uuid

from ..core.connection import A2AConnection, A2AConnectionError
from ..core.session import SessionManager, Session
from ..models.requests import TaskSendRequest, MessageSendRequest, Message, MessagePart
from ..models.responses import TaskResponse, TaskStatus


class SyncClientError(Exception):
    """Exception raised for synchronous client errors."""
    pass


class SyncClient:
    """Synchronous client for communicating with A2A agents."""
    
    def __init__(
        self,
        agent_url: str,
        auth_token: Optional[str] = None,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
        session_timeout_minutes: int = 60
    ):
        """Initialize synchronous A2A client.
        
        Args:
            agent_url: Base URL of the A2A agent
            auth_token: Authentication token if required
            timeout: Request timeout in seconds
            headers: Additional HTTP headers
            session_timeout_minutes: Session expiry timeout in minutes
        """
        self.agent_url = agent_url
        self.connection = A2AConnection(
            base_url=agent_url,
            timeout=timeout,
            headers=headers,
            auth_token=auth_token
        )
        self.session_manager = SessionManager(
            default_timeout_minutes=session_timeout_minutes
        )
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def close(self):
        """Close the client and cleanup resources."""
        self.connection.close()
        self.session_manager.clear_all_sessions()
    
    def send_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        output_mode: str = "text",
        **kwargs
    ) -> TaskResponse:
        """Send a message to the agent and get response.
        
        Args:
            message: Message text to send to the agent
            session_id: Session ID for conversation context (auto-generated if not provided)
            output_mode: Output format mode (default: "text")
            **kwargs: Additional parameters for the request
            
        Returns:
            TaskResponse containing the agent's response
            
        Raises:
            SyncClientError: If the request fails
        """
        try:
            # Generate session ID if not provided
            if session_id is None:
                session_id = str(uuid.uuid4())
            
            # Get or create session
            session = self.session_manager.get_or_create_session(
                session_id=session_id,
                agent_url=self.agent_url
            )
            
            # Create conversation turn
            turn = session.add_turn(input_text=message)
            
            # Prepare request using Kagenti's format
            message_part = MessagePart(kind="text", text=message)
            a2a_message = Message(
                role="user",
                parts=[message_part],
                messageId=str(uuid.uuid4())
            )
            request_params = MessageSendRequest(message=a2a_message).model_dump(by_alias=True)
            
            # Add any additional parameters
            request_params.update(kwargs)
            
            # Try non-streaming method first
            response = self.connection.send_request(
                method="message/send",
                params=request_params,
                request_id=turn.turn_id
            )
            
            # Parse response
            if response.result is None:
                raise SyncClientError("Agent returned empty result")
            
            # Extract text from artifacts structure
            output_text = ""
            if "artifacts" in response.result:
                for artifact in response.result["artifacts"]:
                    if "parts" in artifact:
                        for part in artifact["parts"]:
                            if part.get("kind") == "text" and "text" in part:
                                output_text += part["text"] + "\n"
            
            output_text = output_text.strip()
            if not output_text:
                # Fallback: try to get any text from the response
                output_text = str(response.result)
            
            # Create task response
            task_response = TaskResponse(
                task_id=turn.turn_id,
                session_id=session_id,
                status=TaskStatus.COMPLETED,
                output=output_text,
                metadata=response.result
            )
            
            # Update conversation turn with response
            turn.output_text = task_response.output
            turn.metadata.update(task_response.metadata or {})
            
            return task_response
            
        except A2AConnectionError as e:
            # Update turn with error
            if 'turn' in locals():
                turn.error = str(e)
            raise SyncClientError(f"Connection error: {str(e)}") from e
        except Exception as e:
            # Update turn with error
            if 'turn' in locals():
                turn.error = str(e)
            raise SyncClientError(f"Unexpected error: {str(e)}") from e
    
    def get_conversation_history(
        self,
        session_id: str,
        max_turns: Optional[int] = None
    ) -> list:
        """Get conversation history for a session.
        
        Args:
            session_id: Session ID to retrieve history for
            max_turns: Maximum number of recent turns to return
            
        Returns:
            List of conversation turns
            
        Raises:
            SyncClientError: If session not found
        """
        session = self.session_manager.get_session(session_id)
        if session is None:
            raise SyncClientError(f"Session {session_id} not found")
        
        return session.get_conversation_history(max_turns)
    
    def create_session(
        self,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Session:
        """Create a new conversation session.
        
        Args:
            session_id: Custom session ID (auto-generated if not provided)
            metadata: Initial session metadata
            
        Returns:
            Created Session object
            
        Raises:
            SyncClientError: If session creation fails
        """
        try:
            return self.session_manager.create_session(
                agent_url=self.agent_url,
                session_id=session_id,
                metadata=metadata
            )
        except ValueError as e:
            raise SyncClientError(str(e)) from e
    
    def close_session(self, session_id: str) -> bool:
        """Close a conversation session.
        
        Args:
            session_id: Session ID to close
            
        Returns:
            True if session was found and closed, False otherwise
        """
        return self.session_manager.close_session(session_id)
    
    def list_sessions(self) -> list:
        """Get list of active session IDs.
        
        Returns:
            List of active session IDs
        """
        return self.session_manager.list_active_sessions()
    
    def health_check(self) -> bool:
        """Check if the agent endpoint is healthy.
        
        Returns:
            True if agent is healthy, False otherwise
        """
        return self.connection.health_check()
    
    def cleanup_expired_sessions(self, timeout_minutes: Optional[int] = None) -> list:
        """Remove expired sessions.
        
        Args:
            timeout_minutes: Custom timeout (uses default if not provided)
            
        Returns:
            List of session IDs that were cleaned up
        """
        return self.session_manager.cleanup_expired_sessions(timeout_minutes)