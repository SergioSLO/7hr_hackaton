import { Tabs } from 'expo-router';
import React from 'react';
import {Platform, View} from 'react-native';

import { HapticTab } from '@/components/HapticTab';
import { IconSymbol } from '@/components/ui/IconSymbol';
import TabBarBackground from '@/components/ui/TabBarBackground';
import { Colors } from '@/constants/Colors';
import { useColorScheme } from '@/hooks/useColorScheme';


import MaterialCommunityIcons from '@expo/vector-icons/MaterialCommunityIcons';

export default function TabLayout() {
    const colorScheme = useColorScheme();

    return (
        <Tabs
            screenOptions={{
                tabBarActiveTintColor: Colors[colorScheme ?? 'light'].tint,
                headerShown: false,
                tabBarButton: HapticTab,
                tabBarBackground: TabBarBackground,
                tabBarStyle: Platform.select({
                    ios: {
                        // Use a transparent background on iOS to show the blur effect
                        position: 'absolute',
                    },
                    default: {},
                }),
            }}>
            <Tabs.Screen
                name="index"
                options={{
                    title: 'Datos',
                    tabBarIcon: ({ color }) => <IconSymbol size={28} name="chart.bar" color={color} />,
                }}
            />
            <Tabs.Screen
                name="historial"
                options={{
                    title: 'Historial',
                    tabBarIcon: ({ color }) => <IconSymbol size={28} name="clock.arrow.circlepath" color={color} />,
                }}
            />
      <Tabs.Screen
          name="bot"
          options={{
              title: '',
              tabBarIcon: ({ color }) => (
                  <View
                      style={{
                          backgroundColor: Colors[colorScheme ?? 'light'].background, // color de la barra
                          borderRadius: 43,
                          width: 86,
                          height: 86,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          marginTop: -22, // ajusta para centrar el círculo grande
                      }}
                  >
                      <View
                          style={{
                              backgroundColor: color,
                              borderRadius: 28,
                              width: 56,
                              height: 56,
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                          }}
                      >
                          <MaterialCommunityIcons name="robot-excited-outline" size={40} color={Colors[colorScheme ?? 'light'].icon} />
                      </View>
                  </View>
              ),
          }}
      />
            <Tabs.Screen
                name="preguntas"
                options={{
                    title: 'Preguntas',
                    tabBarIcon: ({ color }) => <IconSymbol size={28} name="questionmark.circle" color={color} />,
                }}
            />
            <Tabs.Screen
                name="resumen"
                options={{
                    title: 'Resumen',
                    tabBarIcon: ({ color }) => <IconSymbol size={28} name="doc.text" color={color} />,
                }}
            />
        </Tabs>
    );
}