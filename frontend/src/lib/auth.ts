// frontend/src/lib/auth.ts
// Simple localStorage-based auth helper

export interface AuthUser {
  _id: string;
  email: string;
  name: string;
  username: string;
  grade_level?: string;
  topic_proficiency?: Record<string, number>;
}

interface AuthData {
  token: string;
  user: AuthUser;
}

const AUTH_KEY = 'conceptpilot_auth';

export function saveAuth(token: string, user: AuthUser): void {
  const data: AuthData = { token, user };
  localStorage.setItem(AUTH_KEY, JSON.stringify(data));
}

export function getAuth(): AuthData | null {
  if (typeof window === 'undefined') return null;
  const raw = localStorage.getItem(AUTH_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthData;
  } catch {
    return null;
  }
}

export function getToken(): string | null {
  return getAuth()?.token ?? null;
}

export function getCurrentUser(): AuthUser | null {
  return getAuth()?.user ?? null;
}

export function getUserId(): string {
  return getAuth()?.user?._id ?? 'user123';
}

export function clearAuth(): void {
  localStorage.removeItem(AUTH_KEY);
}

export function isLoggedIn(): boolean {
  return getAuth() !== null;
}
