# Kagenti A2A Client

A Python client for interacting with Kagenti AI agents via the Agent-to-Agent (A2A) protocol.

## Features

- **JSON-RPC 2.0 over HTTP(S)** - Standard protocol communication
- **Session Management** - Multi-turn conversation support with persistent context
- **Synchronous Communication** - Request/response pattern for real-time interactions
- **Error Handling** - Comprehensive error handling and validation
- **Connection Management** - Automatic connection pooling and cleanup
- **Security** - Authentication token support and input validation

## Installation

```bash
# Install dependencies
pip install -e .
```

## Quick Start

```python
from kagenti_a2a_client import SyncClient

# Create client
with SyncClient(agent_url="http://localhost:8080") as client:
    
    # Check agent health
    if client.health_check():
        print("Agent is healthy!")
    
    # Send message
    response = client.send_message("Hello, how can you help me?")
    print(f"Agent response: {response.output}")
```

## Usage Examples

### Basic Message Exchange

```python
from kagenti_a2a_client import SyncClient, SyncClientError

try:
    with SyncClient(agent_url="http://localhost:8080") as client:
        response = client.send_message(
            message="What can you do?",
            output_mode="text"
        )
        print(f"Status: {response.status}")
        print(f"Output: {response.output}")
        
except SyncClientError as e:
    print(f"Error: {e}")
```

### Multi-turn Conversations

```python
from kagenti_a2a_client import SyncClient

with SyncClient(agent_url="http://localhost:8080") as client:
    
    # Create session for conversation context
    session = client.create_session()
    session_id = session.session_id
    
    # First message
    response1 = client.send_message(
        "I need help with currency conversion",
        session_id=session_id
    )
    
    # Follow-up message with context
    response2 = client.send_message(
        "Convert 100 USD to EUR",
        session_id=session_id
    )
    
    # View conversation history
    history = client.get_conversation_history(session_id)
    for turn in history:
        print(f"User: {turn.input_text}")
        print(f"Agent: {turn.output_text}")
```

### Authentication

```python
from kagenti_a2a_client import SyncClient

# With authentication token
client = SyncClient(
    agent_url="https://api.kagenti.example.com",
    auth_token="your-auth-token-here"
)
```

### Custom Headers and Timeout

```python
from kagenti_a2a_client import SyncClient

client = SyncClient(
    agent_url="http://localhost:8080",
    timeout=60.0,  # 60 seconds
    headers={
        "X-Custom-Header": "value",
        "X-Client-Version": "1.0.0"
    }
)
```

## Architecture

The client is built with a modular architecture:

```
kagenti_a2a_client/
├── core/
│   ├── connection.py      # HTTP/JSON-RPC communication
│   └── session.py         # Session and conversation management
├── communication/
│   └── sync_client.py     # Synchronous client implementation
├── models/
│   ├── requests.py        # Request data models
│   └── responses.py       # Response data models
└── __init__.py           # Main package exports
```

### Core Components

- **A2AConnection**: Handles HTTP communication and JSON-RPC 2.0 protocol
- **SessionManager**: Manages conversation sessions and context
- **SyncClient**: High-level synchronous client interface

### Data Models

- **TaskResponse**: Agent response with status, output, and metadata
- **ConversationTurn**: Individual conversation exchange
- **Session**: Multi-turn conversation context

## API Reference

### SyncClient

The main client class for synchronous communication.

#### Constructor

```python
SyncClient(
    agent_url: str,
    auth_token: Optional[str] = None,
    timeout: float = 30.0,
    headers: Optional[Dict[str, str]] = None,
    session_timeout_minutes: int = 60
)
```

#### Methods

- `send_message(message, session_id=None, output_mode="text")` - Send message to agent
- `create_session(session_id=None, metadata=None)` - Create new conversation session
- `get_conversation_history(session_id, max_turns=None)` - Get conversation history
- `close_session(session_id)` - Close conversation session
- `health_check()` - Check agent health status
- `list_sessions()` - List active session IDs

## Error Handling

The client provides specific exception types:

```python
from kagenti_a2a_client import SyncClientError, A2AConnectionError

try:
    response = client.send_message("Hello")
except SyncClientError as e:
    print(f"Client error: {e}")
except A2AConnectionError as e:
    print(f"Connection error: {e}")
```

## Session Management

Sessions enable multi-turn conversations with context preservation:

- **Automatic expiry** - Sessions expire after inactivity (default: 60 minutes)
- **Conversation history** - Full history of exchanges within a session
- **Metadata support** - Attach custom metadata to sessions
- **Cleanup utilities** - Remove expired sessions automatically

## Examples

See `main.py` for a complete working example demonstrating:

- Client initialization
- Health checking
- Session creation
- Multi-turn conversations
- Error handling
- Resource cleanup

## Development

### Project Structure

This project follows standard Python package conventions with type hints and comprehensive error handling.

### Dependencies

- `httpx` - HTTP client with async support
- `pydantic` - Data validation and serialization
- `typing-extensions` - Enhanced type hints

## Contributing

When contributing to this project:

1. Follow existing code style and patterns
2. Add type hints to all functions
3. Include comprehensive error handling
4. Add unit tests for new functionality
5. Update documentation for new features

## License

This project is open source. See LICENSE file for details.