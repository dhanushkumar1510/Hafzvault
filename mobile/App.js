import React, { useCallback, useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import * as SplashScreen from 'expo-splash-screen';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import AnimatedSplash from './src/components/AnimatedSplash';
import { CONFIG_ERROR } from './src/config';
import { AuthProvider, useAuth } from './src/context/AuthContext';
import RootNavigator from './src/navigation/RootNavigator';
import { colors, spacing } from './src/theme';

SplashScreen.preventAutoHideAsync().catch(() => {});

const MIN_SPLASH_MS = 1400;

function Root() {
  const { status } = useAuth();
  const [minElapsed, setMinElapsed] = useState(false);
  const [splashDone, setSplashDone] = useState(false);
  const finish = useCallback(() => setSplashDone(true), []);

  useEffect(() => {
    const t = setTimeout(() => setMinElapsed(true), MIN_SPLASH_MS);
    return () => clearTimeout(t);
  }, []);

  return (
    <View style={styles.fill}>
      <RootNavigator />
      {!splashDone && <AnimatedSplash ready={status !== 'loading' && minElapsed} onFinished={finish} />}
    </View>
  );
}

function ConfigProblem() {
  useEffect(() => {
    SplashScreen.hideAsync().catch(() => {});
  }, []);
  return (
    <View style={styles.config}>
      <Text style={styles.configTitle}>HafzVault is not configured</Text>
      <Text style={styles.configText}>{CONFIG_ERROR}</Text>
    </View>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <StatusBar style="light" />
      {CONFIG_ERROR ? (
        <ConfigProblem />
      ) : (
        <AuthProvider>
          <Root />
        </AuthProvider>
      )}
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  fill: { flex: 1, backgroundColor: colors.white },
  config: { flex: 1, backgroundColor: colors.forest, alignItems: 'center', justifyContent: 'center', padding: spacing.xxl },
  configTitle: { color: colors.white, fontSize: 20, fontWeight: '800', marginBottom: spacing.md },
  configText: { color: colors.goldLight, fontSize: 15, textAlign: 'center', lineHeight: 22 },
});
