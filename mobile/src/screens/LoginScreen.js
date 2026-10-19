import React, { useEffect, useRef, useState } from 'react';
import { Animated, Easing, Keyboard, KeyboardAvoidingView, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import Banner from '../components/Banner';
import Button from '../components/Button';
import Logo from '../components/Logo';
import TextField from '../components/TextField';
import { useAuth } from '../context/AuthContext';
import { colors, radius, spacing, type } from '../theme';
import { validateEmail, validateUsername } from '../utils/validation';

let firstShow = true; // wait for the splash on cold start only; animate immediately after logout

export default function LoginScreen() {
  const insets = useSafeAreaInsets();
  const { login, createAccount, notice } = useAuth();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [errors, setErrors] = useState({});
  const [banner, setBanner] = useState(notice ? { type: 'info', text: notice } : null);
  const [confirmCreate, setConfirmCreate] = useState(false);
  const [loading, setLoading] = useState(false);
  const emailRef = useRef(null);
  const mounted = useRef(true);

  const hero = useRef(new Animated.Value(0)).current;
  const sheet = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    mounted.current = true;
    const delay = firstShow ? 1000 : 0;
    firstShow = false;
    Animated.sequence([
      Animated.delay(delay),
      Animated.spring(hero, { toValue: 1, friction: 6, useNativeDriver: true }),
      Animated.timing(sheet, { toValue: 1, duration: 450, easing: Easing.out(Easing.cubic), useNativeDriver: true }),
    ]).start();
    return () => {
      mounted.current = false;
    };
  }, [hero, sheet]);

  const heroStyle = { opacity: hero, transform: [{ scale: hero.interpolate({ inputRange: [0, 1], outputRange: [0.7, 1] }) }] };
  const sheetStyle = { opacity: sheet, transform: [{ translateY: sheet.interpolate({ inputRange: [0, 1], outputRange: [40, 0] }) }] };

  const edit = (setter, field) => (value) => {
    setter(value);
    setConfirmCreate(false);
    setBanner(null);
    if (errors[field]) setErrors((e) => ({ ...e, [field]: null }));
  };

  const submit = async (create = false) => {
    const found = { username: validateUsername(username), email: validateEmail(email) };
    setErrors(found);
    if (found.username || found.email) return;
    Keyboard.dismiss();
    setLoading(true);
    setBanner(null);
    try {
      if (create) {
        await createAccount(username, email);
      } else {
        const result = await login(username, email);
        if (result.needsCreate && mounted.current) setConfirmCreate(true);
      }
    } catch (err) {
      if (!mounted.current) return;
      setBanner({ type: 'error', text: err.message });
      setConfirmCreate(false);
      setErrors((e) => ({ ...e, ...err.fieldErrors }));
    } finally {
      if (mounted.current) setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView style={styles.root} behavior="padding">
      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled" showsVerticalScrollIndicator={false}>
        <Animated.View style={[styles.hero, { paddingTop: insets.top + spacing.xxl }, heroStyle]}>
          <Logo size={112} />
          <Text style={styles.brand}>HafzVault</Text>
          <Text style={styles.tag}>Receipts & warranties, safely kept</Text>
        </Animated.View>

        <Animated.View style={[styles.sheet, { paddingBottom: insets.bottom + spacing.xl }, sheetStyle]}>
          <Text style={type.title}>Open your vault</Text>
          <Text style={[type.small, styles.sub]}>
            Enter your username and email. New here? We&apos;ll offer to create your account.
          </Text>

          <TextField
            label="Username"
            icon="person-outline"
            value={username}
            onChangeText={edit(setUsername, 'username')}
            error={errors.username}
            placeholder="e.g. hafiz_01"
            autoCapitalize="none"
            autoCorrect={false}
            maxLength={30}
            returnKeyType="next"
            onSubmitEditing={() => emailRef.current && emailRef.current.focus()}
            editable={!loading}
          />
          <TextField
            ref={emailRef}
            label="Email address"
            icon="mail-outline"
            value={email}
            onChangeText={edit(setEmail, 'email')}
            error={errors.email}
            placeholder="you@example.com"
            keyboardType="email-address"
            autoComplete="email"
            autoCapitalize="none"
            autoCorrect={false}
            returnKeyType="go"
            onSubmitEditing={() => submit(false)}
            editable={!loading}
          />

          <Banner type={banner && banner.type} text={banner && banner.text} />

          {confirmCreate ? (
            <View style={styles.confirm}>
              <Text style={styles.confirmTitle}>No account with these details yet</Text>
              <Text style={[type.small, styles.confirmText]}>
                Create a new HafzVault account for {username.trim()} ({email.trim().toLowerCase()})?
              </Text>
              <Button title="Create account" variant="gold" loading={loading} onPress={() => submit(true)} />
              <Button title="Edit details" variant="ghost" disabled={loading} onPress={() => setConfirmCreate(false)} style={styles.editBtn} />
            </View>
          ) : (
            <Button title="Continue" loading={loading} onPress={() => submit(false)} />
          )}

          <Text style={styles.note}>
            There is no password or verification. Anyone who knows this username and email can open these records, so keep
            them private.
          </Text>
        </Animated.View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.forest },
  scroll: { flexGrow: 1 },
  hero: { alignItems: 'center', paddingBottom: spacing.xxl },
  brand: { color: colors.white, fontSize: 30, fontWeight: '800', marginTop: spacing.sm, letterSpacing: 0.5 },
  tag: { color: colors.goldLight, fontSize: 14, marginTop: 4 },
  sheet: {
    flex: 1,
    backgroundColor: colors.white,
    borderTopLeftRadius: radius.xl,
    borderTopRightRadius: radius.xl,
    padding: spacing.xl,
  },
  sub: { marginTop: spacing.xs, marginBottom: spacing.xl },
  confirm: { backgroundColor: colors.forestTint, borderRadius: radius.lg, padding: spacing.lg },
  confirmTitle: { fontSize: 16, fontWeight: '700', color: colors.forest },
  confirmText: { marginTop: spacing.xs, marginBottom: spacing.md },
  editBtn: { marginTop: spacing.xs },
  note: { fontSize: 12, color: colors.muted, textAlign: 'center', marginTop: spacing.xl, lineHeight: 17 },
});
