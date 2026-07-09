import api from './axios';
import type { AuthUser } from '../types/auth';

export type LoginPayload = {
  email: string;
  password: string;
};

export type RegisterPayload = {
  email: string;
  password: string;
  role?: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
};

export type RegisterResponse = {
  id: number;
  email: string;
};

export async function login(payload: LoginPayload) {
  const formData = new URLSearchParams();
  formData.set('username', payload.email);
  formData.set('password', payload.password);

  return api.post<LoginResponse>('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
}

export async function register(payload: RegisterPayload) {
  return api.post<RegisterResponse>('/auth/register', {
    email: payload.email,
    password: payload.password,
    role: payload.role ?? 'player',
  });
}

export async function getCurrentUser(token?: string) {
  return api.get<AuthUser>('/auth/me', {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });
}
