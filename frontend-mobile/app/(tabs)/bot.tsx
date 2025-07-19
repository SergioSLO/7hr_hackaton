import { Audio } from 'expo-av';
import { useState } from 'react';
import { StyleSheet, TouchableOpacity } from 'react-native';

import { ThemedView } from '@/components/ThemedView';
import { uploadAudio } from '@/services/api';

export default function BotScreen() {
  const [recording, setRecording] = useState<Audio.Recording | null>(null);

  async function toggleRecording() {
    if (recording) {
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setRecording(null);
      if (uri) {
        try {
          await uploadAudio(uri);
        } catch (e) {
          console.warn('Failed to upload recording', e);
        }
      }
    } else {
      const { status } = await Audio.requestPermissionsAsync();
      if (status === 'granted') {
        const rec = new Audio.Recording();
        await rec.prepareToRecordAsync(
          Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY
        );
        await rec.startAsync();
        setRecording(rec);
      }
    }
  }

  return (
    <ThemedView style={styles.container}>
      <TouchableOpacity onPress={toggleRecording} style={styles.button} />
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  button: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#ffffff',
  },
});
