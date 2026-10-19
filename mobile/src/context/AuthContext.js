import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import { accountApi, setIdentity } from '../services/api';
import { clearSession, loadSession, saveSession } from '../storage/session';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [state, setState] = useState({ status: 'loading', account: null, notice: null });

  const startSession = useCallback(async (account) => {
    await saveSession(account);
    setIdentity(account);
    setState({ status: 'signedIn', account, notice: null });
  }, []);

  // Restore the saved session. We open signed-in immediately so the app also starts offline,
  // then confirm with the server in the background.
  useEffect(() => {
    let alive = true;
    (async () => {
      const saved = await loadSession();
      if (!alive) return;
      if (!saved) {
        setState({ status: 'signedOut', account: null, notice: null });
        return;
      }
      setIdentity(saved);
      setState({ status: 'signedIn', account: saved, notice: null });
      try {
        const fresh = await accountApi.profile();
        if (alive) setState((s) => ({ ...s, account: { ...s.account, ...fresh } }));
      } catch (err) {
        if (err.kind === 'auth' && alive) {
          await clearSession();
          setIdentity(null);
          setState({ status: 'signedOut', account: null, notice: 'Your saved account could not be found. Please sign in again.' });
        } // network/server errors: keep the saved session
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  /** Resolves {needsCreate:true} when the pair is unknown; throws ApiError for mismatches/network errors. */
  const login = useCallback(
    async (username, email) => {
      try {
        const account = await accountApi.lookup(username, email);
        await startSession(account);
        return { needsCreate: false };
      } catch (err) {
        if (err.status === 404 && err.code === 'account_not_found') return { needsCreate: true };
        throw err;
      }
    },
    [startSession]
  );

  const createAccount = useCallback(
    async (username, email) => {
      const account = await accountApi.create(username, email);
      await startSession(account);
    },
    [startSession]
  );

  const refreshProfile = useCallback(async () => {
    const fresh = await accountApi.profile();
    setState((s) => ({ ...s, account: { ...s.account, ...fresh } }));
    return fresh;
  }, []);

  const logout = useCallback(async () => {
    await clearSession();
    setIdentity(null);
    setState({ status: 'signedOut', account: null, notice: null });
  }, []);

  const value = useMemo(
    () => ({ ...state, login, createAccount, refreshProfile, logout }),
    [state, login, createAccount, refreshProfile, logout]
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
