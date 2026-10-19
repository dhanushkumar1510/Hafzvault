// Mirrors the backend rules in vault/serializers.py (username 3-30 chars; email normalised to lowercase).
export const USERNAME_RE = /^[A-Za-z0-9_.-]{3,30}$/;
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export function normalizeEmail(value) {
  return (value || '').trim().toLowerCase();
}

export function validateUsername(value) {
  const v = (value || '').trim();
  if (!v) return 'Enter a username.';
  if (!USERNAME_RE.test(v)) return 'Use 3-30 letters, numbers, dots, underscores or hyphens.';
  return null;
}

export function validateEmail(value) {
  const v = normalizeEmail(value);
  if (!v) return 'Enter your email address.';
  if (v.length > 254 || !EMAIL_RE.test(v)) return 'Enter a valid email address.';
  return null;
}
