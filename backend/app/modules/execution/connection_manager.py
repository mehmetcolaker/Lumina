"""WebSocket connection manager for real-time code execution results.

Maintains a mapping of ``submission_id → list[WebSocket]`` so that when
a Celery worker finishes processing, the result can be pushed to the
correct connected client(s).

Usage (inside the WebSocket endpoint)::

    manager = ConnectionManager()
    await manager.connect(websocket, submission_id)
    # ... listen on Redis Pub/Sub ...
    await manager.disconnect(websocket, submission_id)
"""

import json
import logging
from typing import Optional

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """In-memory registry of active WebSocket connections grouped by
    submission ID.

    Thread-safety note: all methods are called from the same async event
    loop (FastAPI runs WebSocket handlers on the main loop), so no locks
    are needed.
    """

    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, submission_id: str) -> None:
        """Accept and register a new WebSocket connection.

        Args:
            websocket: The FastAPI WebSocket instance.
            submission_id: The UUID of the submission this client is
                           waiting for.
        """
        await websocket.accept()
        self._connections.setdefault(submission_id, []).append(websocket)
        logger.info(
            "WS connected for submission %s (total %d listeners)",
            submission_id,
            len(self._connections[submission_id]),
        )

    async def disconnect(self, websocket: WebSocket, submission_id: str) -> None:
        """Remove a WebSocket connection from the registry.

        Args:
            websocket: The WebSocket instance to remove.
            submission_id: The associated submission UUID.
        """
        listeners = self._connections.get(submission_id, [])
        if websocket in listeners:
            listeners.remove(websocket)
        if not listeners:
            self._connections.pop(submission_id, None)
        logger.info(
            "WS disconnected for submission %s", submission_id,
        )

    async def send_personal_message(
        self,
        submission_id: str,
        message: dict,
    ) -> bool:
        """Send a JSON message to *all* listeners registered for a
        submission, then close each connection.

        Args:
            submission_id: The submission UUID whose listeners to notify.
            message: A JSON-serialisable dict to send.

        Returns:
            True if at least one listener was notified.
        """
        listeners = self._connections.pop(submission_id, [])
        if not listeners:
            return False

        payload = json.dumps(message)
        for ws in listeners:
            try:
                await ws.send_text(payload)
                await ws.close()
            except Exception:
                logger.warning(
                    "Failed to send WS message for %s", submission_id,
                )
        return True

    @property
    def active_connections(self) -> int:
        """Return the total number of registered WebSocket connections."""
        return sum(len(v) for v in self._connections.values())


# Module-level singleton – imported and used by both the WS endpoint
# and the background Pub/Sub listener (if any).
manager = ConnectionManager()
