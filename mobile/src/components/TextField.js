import React, { forwardRef, useState } from 'react';
import { StyleSheet, Text, TextInput, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import { colors, radius, spacing, type } from '../theme';

const TextField = forwardRef(function TextField({ label, error, icon, style, ...inputProps }, ref) {
  const [focused, setFocused] = useState(false);
  const borderColor = error ? colors.danger : focused ? colors.gold : colors.border;
  return (
    <View style={[styles.wrap, style]}>
      {label ? <Text style={[type.label, styles.label]}>{label}</Text> : null}
      <View style={[styles.box, { borderColor }, focused && styles.focused]}>
        {icon ? <Ionicons name={icon} size={20} color={error ? colors.danger : colors.forest} style={styles.icon} /> : null}
        <TextInput
          ref={ref}
          style={styles.input}
          placeholderTextColor="#8A978F"
          accessibilityLabel={label}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          {...inputProps}
        />
      </View>
      {error ? <Text style={styles.error}>{error}</Text> : null}
    </View>
  );
});

export default TextField;

const styles = StyleSheet.create({
  wrap: { marginBottom: spacing.lg },
  label: { marginBottom: spacing.xs + 2 },
  box: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1.5,
    borderRadius: radius.md,
    backgroundColor: colors.white,
    paddingHorizontal: spacing.md,
    minHeight: 50,
  },
  focused: { borderWidth: 2 },
  icon: { marginRight: spacing.sm },
  input: { flex: 1, fontSize: 16, color: colors.text, paddingVertical: spacing.md },
  error: { color: colors.danger, fontSize: 13, marginTop: spacing.xs + 1 },
});
