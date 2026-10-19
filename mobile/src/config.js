// The ONLY place the API URL is read. Everything else imports from here.
const raw = (process.env.EXPO_PUBLIC_API_URL || '').trim().replace(/\/+$/, '');

export const API_BASE_URL = raw ? `${raw}/api` : '';

function configError() {
  if (!raw) {
    return (
      'EXPO_PUBLIC_API_URL is not set. Copy mobile/.env.example to mobile/.env, ' +
      'set the server URL, then restart with: npx expo start -c'
    );
  }
  if (!__DEV__ && !raw.startsWith('https://')) {
    return 'Release builds must use an HTTPS API URL (EXPO_PUBLIC_API_URL).';
  }
  return null;
}

export const CONFIG_ERROR = configError();
