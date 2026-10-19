import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';

import HomeScreen from '../screens/HomeScreen';
import ProfileScreen from '../screens/ProfileScreen';
import ReceiptsScreen from '../screens/ReceiptsScreen';
import { colors } from '../theme';

const Tab = createBottomTabNavigator();

const ICONS = {
  Home: ['home', 'home-outline'],
  Receipts: ['receipt', 'receipt-outline'],
  Profile: ['person', 'person-outline'],
};

export default function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerStyle: { backgroundColor: colors.forest },
        headerTintColor: colors.white,
        headerTitleStyle: { fontWeight: '700' },
        tabBarStyle: { backgroundColor: colors.forest, borderTopColor: colors.forestDark },
        tabBarActiveTintColor: colors.gold,
        tabBarInactiveTintColor: 'rgba(255,255,255,0.65)',
        tabBarLabelStyle: { fontWeight: '600' },
        tabBarIcon: ({ focused, color, size }) => (
          <Ionicons name={ICONS[route.name][focused ? 0 : 1]} size={size} color={color} />
        ),
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} options={{ title: 'HafzVault' }} />
      <Tab.Screen name="Receipts" component={ReceiptsScreen} options={{ title: 'All receipts' }} />
      <Tab.Screen name="Profile" component={ProfileScreen} options={{ title: 'Profile' }} />
    </Tab.Navigator>
  );
}
