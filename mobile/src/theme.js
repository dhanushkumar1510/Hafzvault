export const colors = {
  forest: '#14532D',
  forestDark: '#0E3D21',
  forestMid: '#1F6B3A',
  forestTint: '#EAF3EC',
  gold: '#C9A227',
  goldLight: '#F4E7B3',
  goldDark: '#9A7A12',
  white: '#FFFFFF',
  text: '#12241A',
  muted: '#5B6B61',
  border: '#DDE5DF',
  danger: '#B42318',
  dangerTint: '#FDECEA',
};

export const spacing = { xs: 4, sm: 8, md: 12, lg: 16, xl: 24, xxl: 32 };
export const radius = { sm: 8, md: 12, lg: 16, xl: 28, pill: 999 };

export const type = {
  title: { fontSize: 26, fontWeight: '800', color: colors.text },
  heading: { fontSize: 18, fontWeight: '700', color: colors.text },
  body: { fontSize: 15, color: colors.text },
  small: { fontSize: 13, color: colors.muted },
  label: { fontSize: 13, fontWeight: '600', color: colors.text },
};

export const shadow = {
  shadowColor: '#000',
  shadowOpacity: 0.08,
  shadowRadius: 10,
  shadowOffset: { width: 0, height: 4 },
  elevation: 3,
};

export const card = {
  backgroundColor: colors.white,
  borderRadius: radius.lg,
  borderWidth: 1,
  borderColor: colors.border,
  padding: spacing.lg,
  ...shadow,
};
