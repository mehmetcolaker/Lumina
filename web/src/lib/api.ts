/**
 * Lumina API client.
 *
 * Lightweight fetch wrapper that:
 *   - Reads `VITE_API_URL` (defaults to `http://localhost:8000/api/v1`)
 *   - Auto-attaches the JWT from `localStorage` as `Authorization: Bearer …`
 *   - Throws a typed `ApiError` on non-2xx responses
 *
 * Usage:
 *   import { api } from "@/lib/api";
 *   const me = await api.get<UserResponse>("/users/me");
 */

const TOKEN_STORAGE_KEY = "lumina_access_token";

// Vite replaces import.meta.env.VITE_* at build time.
// Fallback ensures SSR / test environments still work.
export const API_URL: string =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";


// -------------------------------------------------------------
// Token storage
// -------------------------------------------------------------

export const tokenStorage = {
  get(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(TOKEN_STORAGE_KEY);
  },
  set(token: string): void {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
  },
  clear(): void {
    if (typeof window === "undefined") return;
    window.localStorage.removeItem(TOKEN_STORAGE_KEY);
  },
};


// -------------------------------------------------------------
// Errors
// -------------------------------------------------------------

export class ApiError extends Error {
  status: number;
  data: unknown;
  constructor(status: number, message: string, data?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}


// -------------------------------------------------------------
// Core fetcher
// -------------------------------------------------------------

interface RequestOptions extends Omit<RequestInit, "body"> {
  /** A JSON-serialisable body. */
  json?: unknown;
  /** Form-encoded body (used by OAuth2 password flow). */
  form?: Record<string, string>;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const url = `${API_URL}${path.startsWith("/") ? path : `/${path}`}`;
  const headers = new Headers(options.headers);

  // Attach JWT if present
  const token = tokenStorage.get();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  let body: BodyInit | undefined;
  if (options.json !== undefined) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(options.json);
  } else if (options.form) {
    headers.set("Content-Type", "application/x-www-form-urlencoded");
    body = new URLSearchParams(options.form).toString();
  }

  const response = await fetch(url, {
    ...options,
    headers,
    body,
  });

  // 204 No Content
  if (response.status === 204) return undefined as T;

  let data: unknown;
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  if (!response.ok) {
    const detail =
      typeof data === "object" && data !== null && "detail" in data
        ? String((data as { detail: unknown }).detail)
        : response.statusText;
    throw new ApiError(response.status, detail, data);
  }

  return data as T;
}


// -------------------------------------------------------------
// Typed convenience methods
// -------------------------------------------------------------

export const api = {
  get<T>(path: string, init?: RequestOptions): Promise<T> {
    return request<T>(path, { ...init, method: "GET" });
  },
  post<T>(path: string, body?: unknown, init?: RequestOptions): Promise<T> {
    return request<T>(path, { ...init, method: "POST", json: body });
  },
  postForm<T>(path: string, form: Record<string, string>, init?: RequestOptions): Promise<T> {
    return request<T>(path, { ...init, method: "POST", form });
  },
  put<T>(path: string, body?: unknown, init?: RequestOptions): Promise<T> {
    return request<T>(path, { ...init, method: "PUT", json: body });
  },
  patch<T>(path: string, body?: unknown, init?: RequestOptions): Promise<T> {
    return request<T>(path, { ...init, method: "PATCH", json: body });
  },
  delete<T = void>(path: string, init?: RequestOptions): Promise<T> {
    return request<T>(path, { ...init, method: "DELETE" });
  },
};
