"""Core A2A connection handler using JSON-RPC 2.0 over HTTP."""

import httpx
import json
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

from ..models.requests import JsonRpcRequest
from ..models.responses import JsonRpcResponse, JsonRpcError


class A2AConnectionError(Exception):
    """Exception raised for A2A connection errors."""
    
    def __init__(self, message: str, error_code: Optional[int] = None):
        super().__init__(message)
        self.error_code = error_code


class A2AConnection:
    """Handles HTTP connections and JSON-RPC 2.0 communication with A2A agents."""
    
    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
        auth_token: Optional[str] = None
    ):
        """Initialize A2A connection.
        
        Args:
            base_url: Base URL of the A2A agent endpoint
            timeout: Request timeout in seconds
            headers: Additional HTTP headers to include
            auth_token: Authentication token if required
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Build default headers
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "kagenti-a2a-client/0.1.0"
        }
        
        if headers:
            default_headers.update(headers)
            
        if auth_token:
            default_headers["Authorization"] = f"Bearer {auth_token}"
            
        # Initialize HTTP client
        self._client = httpx.Client(
            headers=default_headers,
            timeout=timeout,
            follow_redirects=True
        )
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def close(self):
        """Close the HTTP client."""
        if hasattr(self, '_client'):
            self._client.close()
    
    def send_request(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        request_id: Optional[Union[str, int]] = None,
        endpoint: str = ""
    ) -> JsonRpcResponse:
        """Send a JSON-RPC 2.0 request to the agent.
        
        Args:
            method: JSON-RPC method name
            params: Method parameters
            request_id: Request ID (auto-generated if not provided)
            endpoint: Additional endpoint path (appended to base_url)
            
        Returns:
            JsonRpcResponse object
            
        Raises:
            A2AConnectionError: If the request fails or returns an error
        """
        # Create JSON-RPC request
        rpc_request = JsonRpcRequest(
            method=method,
            params=params,
            id=request_id
        )
        
        # Build full URL
        url = self.base_url
        if endpoint:
            url = urljoin(url + '/', endpoint.lstrip('/'))
        
        try:
            # Send HTTP request
            response = self._client.post(
                url,
                content=rpc_request.model_dump_json(by_alias=True, exclude_none=True)
            )
            response.raise_for_status()
            
            # Parse JSON-RPC response
            if not response.text.strip():
                raise A2AConnectionError("Empty response from server")
            
            response_data = response.json()
            rpc_response = JsonRpcResponse(**response_data)
            
            # Check for JSON-RPC errors
            if rpc_response.error:
                raise A2AConnectionError(
                    f"JSON-RPC error: {rpc_response.error.message}",
                    error_code=rpc_response.error.code
                )
            
            return rpc_response
            
        except httpx.HTTPStatusError as e:
            raise A2AConnectionError(
                f"HTTP error {e.response.status_code}: {e.response.text}"
            ) from e
        except httpx.RequestError as e:
            raise A2AConnectionError(f"Request error: {str(e)}") from e
        except json.JSONDecodeError as e:
            raise A2AConnectionError(f"Invalid JSON response: {str(e)}") from e
        except Exception as e:
            raise A2AConnectionError(f"Unexpected error: {str(e)}") from e
    
    def send_streaming_request(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        request_id: Optional[Union[str, int]] = None,
        endpoint: str = ""
    ) -> httpx.Response:
        """Send a streaming JSON-RPC 2.0 request to the agent.
        
        Args:
            method: JSON-RPC method name
            params: Method parameters
            request_id: Request ID (auto-generated if not provided)
            endpoint: Additional endpoint path
            
        Returns:
            Raw HTTP response for streaming processing
            
        Raises:
            A2AConnectionError: If the request fails
        """
        # Create JSON-RPC request
        rpc_request = JsonRpcRequest(
            method=method,
            params=params,
            id=request_id
        )
        
        # Build full URL
        url = self.base_url
        if endpoint:
            url = urljoin(url + '/', endpoint.lstrip('/'))
        
        try:
            # Send streaming HTTP request
            response = self._client.stream(
                "POST",
                url,
                content=rpc_request.model_dump_json(by_alias=True, exclude_none=True)
            )
            response.raise_for_status()
            return response
            
        except httpx.HTTPStatusError as e:
            raise A2AConnectionError(
                f"HTTP error {e.response.status_code}: {e.response.text}"
            ) from e
        except httpx.RequestError as e:
            raise A2AConnectionError(f"Request error: {str(e)}") from e
        except Exception as e:
            raise A2AConnectionError(f"Unexpected error: {str(e)}") from e
    
    def health_check(self) -> bool:
        """Check if the agent endpoint is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Just check if we can make an HTTP connection
            response = self._client.get(f"{self.base_url}")
            return response.status_code in [200, 404, 405]  # Accept common valid responses
        except Exception:
            return False