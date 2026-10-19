import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import { colors, spacing, type } from '../theme';

// Temporary stand-in used only by Home and Receipts until Phase 3 replaces those screens.
export default function PlaceholderScreen({ icon, title, text }) {
  return (
    <View style={styles.root}>
      <View style={styles.badge}>
        <Ionicons name={icon} size={36} color={colors.forest} />
      </View>
      <Text style={[type.heading, styles.title]}>{title}</Text>
      <Text style={[type.small, styles.text]}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.white, alignItems: 'center', justifyContent: 'center', padding: spacing.xxl },
  badge: { width: 80, height: 80, borderRadius: 40, backgroundColor: colors.goldLight, alignItems: 'center', justifyContent: 'center', marginBottom: spacing.lg },
  title: { marginBottom: spacing.sm },
  text: { textAlign: 'center' },
});
