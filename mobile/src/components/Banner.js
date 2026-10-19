import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import { colors, radius, spacing } from '../theme';

const TONES = {
  error: { bg: colors.dangerTint, fg: colors.danger, icon: 'alert-circle' },
  info: { bg: colors.forestTint, fg: colors.forest, icon: 'information-circle' },
  success: { bg: colors.forestTint, fg: colors.forest, icon: 'checkmark-circle' },
  warning: { bg: colors.goldLight, fg: colors.goldDark, icon: 'cloud-offline' },
};

export default function Banner({ type = 'info', text, style }) {
  if (!text) return null;
  const t = TONES[type] || TONES.info;
  return (
    <View accessibilityRole="alert" style={[styles.box, { backgroundColor: t.bg }, style]}>
      <Ionicons name={t.icon} size={20} color={t.fg} style={styles.icon} />
      <Text style={[styles.text, { color: t.fg }]}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  box: { flexDirection: 'row', alignItems: 'flex-start', padding: spacing.md, borderRadius: radius.md, marginBottom: spacing.lg },
  icon: { marginRight: spacing.sm, marginTop: 1 },
  text: { flex: 1, fontSize: 14, lineHeight: 20, fontWeight: '500' },
});
