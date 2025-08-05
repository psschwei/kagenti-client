"""Request models for A2A protocol communication."""

from typing import Any, Dict, Optional, Union, Literal
from pydantic import BaseModel, Field
import uuid


class JsonRpcRequest(BaseModel):
    """Base JSON-RPC 2.0 request model."""
    
    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Union[str, int] = Field(default_factory=lambda: str(uuid.uuid4()))


class MessagePart(BaseModel):
    """Part of a message with specific content type."""
    
    kind: str
    text: Optional[str] = None
    data: Optional[Any] = None


class Message(BaseModel):
    """A2A message structure."""
    
    role: str
    parts: list[MessagePart]
    messageId: str = Field(alias="messageId")
    
    class Config:
        populate_by_name = True


class MessageSendRequest(BaseModel):
    """Request model for message/send method."""
    
    message: Message
    
    class Config:
        populate_by_name = True


# Keep the old class for backwards compatibility
class TaskSendRequest(BaseModel):
    """Request model for message/send method."""
    
    session_id: str = Field(alias="sessionId")
    message: str
    output_mode: str = Field(default="text", alias="outputMode")
    
    class Config:
        populate_by_name = True


class TaskSendSubscribeRequest(BaseModel):
    """Request model for tasks/sendSubscribe method (streaming)."""
    
    session_id: str = Field(alias="sessionId")
    input_text: str = Field(alias="inputText")
    output_mode: str = Field(default="text", alias="outputMode")
    webhook_url: Optional[str] = Field(default=None, alias="webhookUrl")
    
    class Config:
        populate_by_name = True


class AgentCardRequest(BaseModel):
    """Request model for retrieving agent capabilities."""
    
    agent_id: Optional[str] = Field(default=None, alias="agentId")
    
    class Config:
        populate_by_name = True