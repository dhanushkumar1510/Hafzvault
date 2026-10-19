import React from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import { colors, radius, spacing } from '../theme';

const VARIANTS = {
  primary: { bg: colors.forest, fg: colors.white, border: colors.forest, ripple: '#ffffff33' },
  gold: { bg: colors.gold, fg: colors.forestDark, border: colors.gold, ripple: '#00000022' },
  outline: { bg: colors.white, fg: colors.forest, border: colors.forest, ripple: '#14532D22' },
  danger: { bg: colors.white, fg: colors.danger, border: colors.danger, ripple: '#B4231822' },
  ghost: { bg: 'transparent', fg: colors.forest, border: 'transparent', ripple: '#14532D22' },
};

export default function Button({ title, onPress, variant = 'primary', loading = false, disabled = false, icon, style, testID }) {
  const v = VARIANTS[variant];
  const inactive = disabled || loading;
  return (
    <Pressable
      testID={testID}
      accessibilityRole="button"
      accessibilityLabel={title}
      accessibilityState={{ disabled: inactive, busy: loading }}
      onPress={inactive ? undefined : onPress}
      android_ripple={{ color: v.ripple }}
      style={({ pressed }) => [
        styles.base,
        { backgroundColor: v.bg, borderColor: v.border },
        pressed && { opacity: 0.88 },
        inactive && { opacity: 0.6 },
        style,
      ]}
    >
      {loading ? (
        <ActivityIndicator color={v.fg} />
      ) : (
        <>
          {icon ? <Ionicons name={icon} size={18} color={v.fg} style={styles.icon} /> : null}
          <Text style={[styles.text, { color: v.fg }]}>{title}</Text>
        </>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    minHeight: 50,
    borderRadius: radius.md,
    borderWidth: 1.5,
    paddingHorizontal: spacing.xl,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  text: { fontSize: 16, fontWeight: '700' },
  icon: { marginRight: spacing.sm },
});
