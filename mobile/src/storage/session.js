import AsyncStorage from '@react-native-async-storage/async-storage';

const KEY = 'hafzvault.session.v1';

export async function loadSession() {
  try {
    const raw = await AsyncStorage.getItem(KEY);
    if (!raw) return null;
    const s = JSON.parse(raw);
    return s && s.id && s.username && s.email ? s : null;
  } catch {
    return null;
  }
}

export async function saveSession(account) {
  const { id, username, email, created_at } = account;
  await AsyncStorage.setItem(KEY, JSON.stringify({ id, username, email, created_at }));
}

export async function clearSession() {
  await AsyncStorage.removeItem(KEY);
}
