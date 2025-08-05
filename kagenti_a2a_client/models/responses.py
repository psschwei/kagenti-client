"""Response models for A2A protocol communication."""

from typing import Any, Dict, Optional, Union, List
from pydantic import BaseModel, Field
from enum import Enum


class JsonRpcError(BaseModel):
    """JSON-RPC 2.0 error model."""
    
    code: int
    message: str
    data: Optional[Any] = None


class JsonRpcResponse(BaseModel):
    """Base JSON-RPC 2.0 response model."""
    
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    result: Optional[Any] = None
    error: Optional[JsonRpcError] = None


class TaskStatus(str, Enum):
    """Task execution status."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskResponse(BaseModel):
    """Response model for task execution."""
    
    task_id: str = Field(alias="taskId")
    session_id: str = Field(alias="sessionId")
    status: TaskStatus
    output: Optional[str] = None
    error_message: Optional[str] = Field(default=None, alias="errorMessage")
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        populate_by_name = True


class StreamingUpdate(BaseModel):
    """Model for streaming task updates."""
    
    task_id: str = Field(alias="taskId")
    session_id: str = Field(alias="sessionId")
    status: TaskStatus
    partial_output: Optional[str] = Field(default=None, alias="partialOutput")
    timestamp: Optional[str] = None
    
    class Config:
        populate_by_name = True


class AgentCapability(BaseModel):
    """Model for agent capability description."""
    
    name: str
    description: str
    input_types: List[str] = Field(alias="inputTypes")
    output_types: List[str] = Field(alias="outputTypes")
    
    class Config:
        populate_by_name = True


class AgentCard(BaseModel):
    """Model for agent card (capabilities and metadata)."""
    
    agent_id: str = Field(alias="agentId")
    name: str
    description: str
    version: str
    capabilities: List[AgentCapability]
    endpoint_url: str = Field(alias="endpointUrl")
    supported_protocols: List[str] = Field(alias="supportedProtocols")
    
    class Config:
        populate_by_name = True