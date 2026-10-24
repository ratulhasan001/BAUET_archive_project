import { API_BASE } from "./config.js";

const TOKEN_KEY = "archive.token";
const USER_KEY = "archive.user";

export const session = {
  get token() {
    return localStorage.getItem(TOKEN_KEY);
  },
  get user() {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  },
  save(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },
  clear() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },
  get isLoggedIn() {
    return Boolean(this.token);
  },
};

export class ApiError extends Error {
  constructor(status, data) {
    super(ApiError.messageFrom(data) || `Request failed (${status})`);
    this.status = status;
    this.data = data;
  }

  static messageFrom(data) {
    if (!data) return "";
    if (typeof data === "string") return data;
    if (data.detail) return data.detail;
    if (data.non_field_errors) return data.non_field_errors.join(" ");
    return "";
  }
}

export async function api(path, { method = "GET", body, query } = {}) {
  const url = new URL(`${API_BASE}${path}`);
  Object.entries(query || {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") url.searchParams.set(key, value);
  });

  const headers = { Accept: "application/json" };
  if (session.token) headers.Authorization = `Token ${session.token}`;
  if (body && !(body instanceof FormData)) headers["Content-Type"] = "application/json";

  const response = await fetch(url, {
    method,
    headers,
    body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
  });

  if (response.status === 401 && session.token) session.clear();
  if (response.status === 204) return null;

  const data = await response.json().catch(() => null);
  if (!response.ok) throw new ApiError(response.status, data);
  return data;
}
