// Pure module (no React Native / axios imports) so it can be unit-tested anywhere.
export class ApiError extends Error {
  constructor({ kind, status = null, code = null, message, fieldErrors = {} }) {
    super(message);
    this.name = 'ApiError';
    this.kind = kind; // 'network' | 'timeout' | 'auth' | 'server' | 'http'
    this.status = status;
    this.code = code;
    this.fieldErrors = fieldErrors;
  }
}

function firstText(value) {
  if (Array.isArray(value)) return firstText(value[0]);
  if (value && typeof value === 'object') return firstText(Object.values(value)[0]);
  return typeof value === 'string' ? value : null;
}

export function toApiError(err) {
  if (err instanceof ApiError) return err;
  const res = err && err.response;
  if (res) {
    const data = res.data && typeof res.data === 'object' ? res.data : {};
    const fieldErrors = {};
    Object.entries(data).forEach(([key, value]) => {
      if (key === 'detail' || key === 'code') return;
      const text = firstText(value);
      if (text) fieldErrors[key] = text;
    });
    const message =
      (typeof data.detail === 'string' && data.detail) ||
      Object.values(fieldErrors)[0] ||
      (res.status >= 500
        ? 'Something went wrong on the server. Please try again.'
        : `Request failed (${res.status}).`);
    const kind = res.status === 401 ? 'auth' : res.status >= 500 ? 'server' : 'http';
    return new ApiError({ kind, status: res.status, code: data.code || null, message, fieldErrors });
  }
  if (err && (err.code === 'ECONNABORTED' || err.code === 'ETIMEDOUT')) {
    return new ApiError({
      kind: 'timeout',
      message: 'The server is taking too long to respond. It may be waking up, so please try again in a moment.',
    });
  }
  return new ApiError({
    kind: 'network',
    message: "Can't reach HafzVault. Check your internet connection and try again.",
  });
}
