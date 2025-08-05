"""Communication components for A2A client."""

from .sync_client import SyncClient, SyncClientError

__all__ = ["SyncClient", "SyncClientError"]