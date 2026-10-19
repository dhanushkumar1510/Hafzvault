import React from 'react';
import { Image } from 'react-native';

export default function Logo({ size = 120, style }) {
  return (
    <Image
      source={require('../../assets/splash-icon.png')}
      style={[{ width: size, height: size }, style]}
      resizeMode="contain"
      accessibilityLabel="HafzVault logo"
    />
  );
}
