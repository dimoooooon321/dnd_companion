import type { AuthSession, AuthUser } from '../types/auth';

export const AUTH_SESSION_STORAGE_KEY = 'dnd_companion_auth_session';
export const AUTH_INVALIDATED_EVENT = 'dnd-companion:auth-invalidated';

type StoredAuthSession = {
  token: string;
  user: AuthUser;
};

export function readAuthSession(): AuthSession | null {
  if (typeof window === 'undefined') {
    return null;
  }

  const rawSession = window.localStorage.getItem(AUTH_SESSION_STORAGE_KEY);

  if (!rawSession) {
    return null;
  }

  try {
    const parsed = JSON.parse(rawSession) as Partial<StoredAuthSession>;

    if (
      typeof parsed.token !== 'string' ||
      parsed.user == null ||
      typeof parsed.user.id !== 'number' ||
      typeof parsed.user.email !== 'string' ||
      typeof parsed.user.role !== 'string'
    ) {
      return null;
    }

    return {
      token: parsed.token,
      user: parsed.user,
    };
  } catch {
    return null;
  }
}

export function writeAuthSession(session: AuthSession) {
  window.localStorage.setItem(AUTH_SESSION_STORAGE_KEY, JSON.stringify(session));
}

export function clearAuthSession() {
  window.localStorage.removeItem(AUTH_SESSION_STORAGE_KEY);
}

export function notifyAuthInvalidated() {
  window.dispatchEvent(new Event(AUTH_INVALIDATED_EVENT));
}
