import { createContext, useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import api from '../api/axios';
import {
  AUTH_INVALIDATED_EVENT,
  clearAuthSession,
  readAuthSession,
  writeAuthSession,
} from '../lib/authSession';
import type { AuthContextValue, AuthSession, AuthUser } from '../types/auth';

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

type AuthProviderProps = {
  children: ReactNode;
};

export function AuthProvider({ children }: AuthProviderProps) {
  const storedSession = readAuthSession();
  const [token, setToken] = useState<string | null>(storedSession?.token ?? null);
  const [user, setUser] = useState<AuthUser | null>(storedSession?.user ?? null);
  const [isLoading, setIsLoading] = useState(Boolean(storedSession?.token));

  const logout = useCallback(() => {
    clearAuthSession();
    setToken(null);
    setUser(null);
    setIsLoading(false);
  }, []);

  const login = useCallback((session: AuthSession) => {
    writeAuthSession(session);
    setToken(session.token);
    setUser(session.user);
    setIsLoading(false);
  }, []);

  const refreshSession = useCallback(async () => {
    if (!token) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);

    try {
      const { data } = await api.get<AuthUser>('/auth/me');
      setUser(data);
      writeAuthSession({
        token,
        user: data,
      });
    } catch {
      logout();
    } finally {
      setIsLoading(false);
    }
  }, [logout, token]);

  useEffect(() => {
    void refreshSession();
  }, [refreshSession]);

  useEffect(() => {
    const handleAuthInvalidated = () => {
      logout();
    };

    window.addEventListener(AUTH_INVALIDATED_EVENT, handleAuthInvalidated);

    return () => {
      window.removeEventListener(AUTH_INVALIDATED_EVENT, handleAuthInvalidated);
    };
  }, [logout]);

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token),
      isLoading,
      login,
      logout,
      refreshSession,
    }),
    [isLoading, login, logout, refreshSession, token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
