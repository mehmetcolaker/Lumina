/**
 * Authentication context backed by the Lumina FastAPI backend.
 *
 * Provides:
 *   - `user`        — the currently authenticated user (or null)
 *   - `loading`     — true while the initial /users/me check is in flight
 *   - `signIn`      — POST /auth/login (form-encoded)
 *   - `signUp`      — POST /auth/register (JSON)
 *   - `signOut`     — clears the JWT and refetches /users/me
 *   - `refresh`     — manually re-validate the current session
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { api, ApiError, tokenStorage } from "@/lib/api";
import type { TokenResponse, UserResponse } from "@/lib/api-types";

interface AuthContextValue {
  user: UserResponse | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<UserResponse>;
  signUp: (email: string, password: string) => Promise<UserResponse>;
  signOut: () => Promise<void>;
  refresh: () => Promise<UserResponse | null>;
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  loading: true,
  signIn: async () => {
    throw new Error("AuthProvider is missing");
  },
  signUp: async () => {
    throw new Error("AuthProvider is missing");
  },
  signOut: async () => {},
  refresh: async () => null,
});


export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async (): Promise<UserResponse | null> => {
    if (!tokenStorage.get()) {
      setUser(null);
      return null;
    }
    try {
      const me = await api.get<UserResponse>("/users/me");
      setUser(me);
      return me;
    } catch (err) {
      // Expired or invalid token — clear it
      if (err instanceof ApiError && err.status === 401) {
        tokenStorage.clear();
      }
      setUser(null);
      return null;
    }
  }, []);

  // Initial session check on mount
  useEffect(() => {
    let cancelled = false;
    (async () => {
      await refresh();
      if (!cancelled) setLoading(false);
    })();
    return () => {
      cancelled = true;
    };
  }, [refresh]);

  const signIn = useCallback(
    async (email: string, password: string): Promise<UserResponse> => {
      const token = await api.postForm<TokenResponse>("/auth/login", {
        username: email,
        password,
      });
      tokenStorage.set(token.access_token);
      const me = await api.get<UserResponse>("/users/me");
      setUser(me);
      return me;
    },
    [],
  );

  const signUp = useCallback(
    async (email: string, password: string): Promise<UserResponse> => {
      const newUser = await api.post<UserResponse>("/auth/register", {
        email,
        password,
      });
      // Auto-login after successful registration
      await signIn(email, password);
      return newUser;
    },
    [signIn],
  );

  const signOut = useCallback(async (): Promise<void> => {
    tokenStorage.clear();
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ user, loading, signIn, signUp, signOut, refresh }),
    [user, loading, signIn, signUp, signOut, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}


export const useAuth = (): AuthContextValue => useContext(AuthContext);
