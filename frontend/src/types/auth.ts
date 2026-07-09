export type AuthUser = {
  id: number;
  email: string;
  role: string;
};

export type AuthSession = {
  token: string;
  user: AuthUser;
};

export type AuthContextValue = {
  token: string | null;
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (session: AuthSession) => void;
  logout: () => void;
  refreshSession: () => Promise<void>;
};
