import React, { useCallback, useState } from 'react';
import { Alert, RefreshControl, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';

import Banner from '../components/Banner';
import Button from '../components/Button';
import { useAuth } from '../context/AuthContext';
import { card, colors, spacing, type } from '../theme';
import { formatLongDate } from '../utils/format';

function Row({ label, value, last }) {
  return (
    <View style={[styles.row, !last && styles.rowBorder]}>
      <Text style={type.small}>{label}</Text>
      <Text style={styles.value} selectable>
        {value}
      </Text>
    </View>
  );
}

export default function ProfileScreen() {
  const { account, refreshProfile, logout } = useAuth();
  const [refreshing, setRefreshing] = useState(false);
  const [stale, setStale] = useState(false);

  const load = useCallback(async () => {
    try {
      await refreshProfile();
      setStale(false);
    } catch {
      setStale(true); // keep showing the saved details
    }
  }, [refreshProfile]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load])
  );

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  const confirmLogout = () =>
    Alert.alert('Log out?', 'You will need to enter your username and email again to open your vault.', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Log out', style: 'destructive', onPress: () => logout() },
    ]);

  if (!account) return null;
  const count = typeof account.receipt_count === 'number' ? String(account.receipt_count) : '—';

  return (
    <ScrollView
      style={styles.root}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[colors.forest]} tintColor={colors.forest} />}
    >
      <View style={styles.header}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>{account.username.charAt(0).toUpperCase()}</Text>
        </View>
        <Text style={type.heading}>{account.username}</Text>
        <Text style={type.small}>{account.email}</Text>
      </View>

      {stale ? <Banner type="warning" text="Couldn't reach the server. Showing your saved account details." /> : null}

      <View style={card}>
        <Row label="Username" value={account.username} />
        <Row label="Email" value={account.email} />
        <Row label="Member since" value={formatLongDate(account.created_at)} />
        <Row label="Receipts stored" value={count} last />
      </View>

      <Banner
        style={styles.notice}
        type="info"
        text="This account is not verified. It is identified only by your username and email, with no password."
      />

      <Button title="Log out" variant="danger" icon="log-out-outline" onPress={confirmLogout} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.white },
  content: { padding: spacing.xl, paddingBottom: spacing.xxl * 2 },
  header: { alignItems: 'center', marginBottom: spacing.xl },
  avatar: { width: 88, height: 88, borderRadius: 44, backgroundColor: colors.gold, alignItems: 'center', justifyContent: 'center', marginBottom: spacing.md },
  avatarText: { fontSize: 38, fontWeight: '800', color: colors.forestDark },
  row: { paddingVertical: spacing.md },
  rowBorder: { borderBottomWidth: 1, borderBottomColor: colors.border },
  value: { fontSize: 16, fontWeight: '600', color: colors.text, marginTop: 2 },
  notice: { marginTop: spacing.lg },
});
