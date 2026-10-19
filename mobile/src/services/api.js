import axios from 'axios';

import { API_BASE_URL } from '../config';
import { normalizeEmail } from '../utils/validation';
import { toApiError } from './apiError';

let identity = null;

/** Called by AuthContext. The backend identifies the account from these two headers. */
export function setIdentity(account) {
  identity = account ? { username: account.username, email: account.email } : null;
}

// Long timeout: Render's free tier can take ~30-60 s to wake up.
export const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 45000,
  headers: { Accept: 'application/json' },
});

client.interceptors.request.use((config) => {
  if (identity) {
    config.headers.set('X-Account-Username', identity.username);
    config.headers.set('X-Account-Email', identity.email);
  }
  return config;
});

export async function request(config) {
  try {
    const res = await client.request(config);
    return res.data;
  } catch (err) {
    throw toApiError(err);
  }
}

export const accountApi = {
  lookup: (username, email) =>
    request({ method: 'post', url: '/accounts/lookup/', data: { username: username.trim(), email: normalizeEmail(email) } }),
  create: (username, email) =>
    request({ method: 'post', url: '/accounts/', data: { username: username.trim(), email: normalizeEmail(email) } }),
  profile: () => request({ method: 'get', url: '/profile/' }),
};
