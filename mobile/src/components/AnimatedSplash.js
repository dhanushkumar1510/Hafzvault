import React, { useEffect, useRef } from 'react';
import { Animated, Easing, StyleSheet, Text, useWindowDimensions } from 'react-native';
import * as SplashScreen from 'expo-splash-screen';

import { colors } from '../theme';
import Logo from './Logo';

// Same background and 200px emblem as the native splash (app.json) so the hand-off is seamless.
export default function AnimatedSplash({ ready, onFinished }) {
  const { height } = useWindowDimensions();
  const scale = useRef(new Animated.Value(0.92)).current;
  const word = useRef(new Animated.Value(0)).current;
  const fade = useRef(new Animated.Value(1)).current;

  const handleLayout = () => {
    SplashScreen.hideAsync().catch(() => {});
    Animated.parallel([
      Animated.spring(scale, { toValue: 1, friction: 5, tension: 60, useNativeDriver: true }),
      Animated.timing(word, { toValue: 1, duration: 600, delay: 250, useNativeDriver: true }),
    ]).start();
  };

  useEffect(() => {
    if (!ready) return;
    Animated.timing(fade, { toValue: 0, duration: 350, easing: Easing.out(Easing.quad), useNativeDriver: true }).start(
      ({ finished }) => finished && onFinished()
    );
  }, [ready, fade, onFinished]);

  return (
    <Animated.View style={[styles.root, { opacity: fade }]} onLayout={handleLayout}>
      <Animated.View style={{ transform: [{ scale }] }}>
        <Logo size={200} />
      </Animated.View>
      <Animated.View style={[styles.wordWrap, { top: height / 2 + 120, opacity: word }]}>
        <Text style={styles.word}>HafzVault</Text>
        <Text style={styles.tag}>Receipts & warranties, safely kept</Text>
      </Animated.View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  root: { ...StyleSheet.absoluteFillObject, backgroundColor: colors.forest, alignItems: 'center', justifyContent: 'center' },
  wordWrap: { position: 'absolute', alignItems: 'center' },
  word: { color: colors.white, fontSize: 30, fontWeight: '800', letterSpacing: 0.5 },
  tag: { color: colors.goldLight, fontSize: 14, marginTop: 6 },
});
