/**
 * WebSocket helper for real-time code execution results.
 *
 * Usage:
 *   import { connectExecutionWS } from "@/lib/ws";
 *
 *   const disconnect = connectExecutionWS(submissionId, token, {
 *     onResult: (data) => console.log(data),
 *     onError: (err) => console.error(err),
 *   });
 *
 *   // Later, to clean up:
 *   disconnect();
 */

import type { ExecutionResult } from "@/lib/api-types";
import { API_URL } from "@/lib/api";

export interface WSCallbacks {
  onResult: (data: ExecutionResult) => void;
  onError?: (error: Event) => void;
}

/**
 * Open a WebSocket connection to listen for a code execution result.
 *
 * @param submissionId - The UUID of the submission to wait for.
 * @param token - A valid JWT access token.
 * @param callbacks - Handlers for result and error events.
 * @returns A cleanup function that closes the WebSocket.
 */
export function connectExecutionWS(
  submissionId: string,
  token: string,
  callbacks: WSCallbacks,
): () => void {
  const wsBase = API_URL.replace(/^http/, "ws");
  const wsUrl = `${wsBase}/execution/ws/${submissionId}?token=${encodeURIComponent(token)}`;

  let ws: WebSocket | null = new WebSocket(wsUrl);

  ws.onopen = () => {
    // Connection established — waiting for result
  };

  ws.onmessage = (event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data) as ExecutionResult;
      callbacks.onResult(data);
    } catch {
      // Non-JSON message — ignore
    }
  };

  ws.onerror = (error: Event) => {
    callbacks.onError?.(error);
  };

  ws.onclose = () => {
    ws = null;
  };

  return () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.close();
    }
    ws = null;
  };
}
