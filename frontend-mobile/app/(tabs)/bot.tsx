import { useEffect, useRef } from 'react';
import {
  useAudioRecorder,
  useAudioRecorderState,
  AudioModule,
  RecordingPresets,
  setAudioModeAsync,
} from 'expo-audio';
import { StyleSheet, TouchableOpacity, Alert, Text } from 'react-native';

import { ThemedView } from '@/components/ThemedView';
import { ThemedText } from '@/components/ThemedText';
import { uploadAudio } from '@/services/api';

export default function BotScreen() {
  // 1. Create recorder & subscribe to its state
  const audioRecorder = useAudioRecorder({
    ...RecordingPresets.HIGH_QUALITY,
    extension: '.wav',
    sampleRate: 44100,
    numberOfChannels: 1,
    bitRate: 128000,
  });
  const recorderState = useAudioRecorderState(audioRecorder);

  // Track last uploaded URL to prevent duplicate uploads
  const lastUploadedUrl = useRef(null);

  // 2. Ask for mic permissions & set audio mode once on mount
  useEffect(() => {
    (async () => {
      try {
        const { granted } = await AudioModule.requestRecordingPermissionsAsync();
        if (!granted) {
          Alert.alert('Permission Required', 'Microphone access is needed to record audio.');
          return;
        }
        await setAudioModeAsync({
          allowsRecording: true,
          playsInSilentMode: true,
          interruptionMode: 'duckOthers', // iOS specific
        });
      } catch (error) {
        console.error('Error setting up audio:', error);
        Alert.alert('Setup Error', 'Failed to initialize audio recording.');
      }
    })();
  }, []);

  // 3. Upload recording when it's complete and we have a new URL
  useEffect(() => {
    if (!recorderState.isRecording &&
        recorderState.url &&
        recorderState.url !== lastUploadedUrl.current) {

      lastUploadedUrl.current = recorderState.url;

      uploadAudio(recorderState.url)
          .then(() => {
            console.log('Audio uploaded successfully');
          })
          .catch((error) => {
            console.warn('Failed to upload recording:', error);
            Alert.alert('Upload Error', 'Failed to upload the recording. Please try again.');
          });
    }
  }, [recorderState.isRecording, recorderState.url]);

  // 4. Toggle recording with proper error handling
  async function toggleRecording() {
    try {
      if (recorderState.isRecording) {
        await audioRecorder.stop();
        console.log("Recording stopped, file saved at:", recorderState.url);
      } else {
        await audioRecorder.prepareToRecordAsync();
        audioRecorder.record();
        console.log("Recording started...");
      }
    } catch (error) {
      console.error('Recording error:', error);
      Alert.alert('Recording Error', 'Failed to start/stop recording. Please try again.');
    }
  }

  // Dynamic button styling based on recording state
  const buttonStyle = [
    styles.button,
    recorderState.isRecording ? styles.buttonRecording : styles.buttonIdle
  ];

  return (
      <ThemedView style={styles.container}>
        <ThemedText style={styles.title}>¿Cómo te puedo ayudar hoy?</ThemedText>
        <ThemedText style={styles.subtitle}>
          Haz click para grabar un gasto o consultar tus gastos
        </ThemedText>

        <TouchableOpacity
            onPress={toggleRecording}
            style={buttonStyle}
            activeOpacity={0.7}
        >
          <Text style={styles.buttonText}>
            {recorderState.isRecording ? '⏹️' : '🎤'}
          </Text>
        </TouchableOpacity>
      </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 50,
    lineHeight: 22,
    opacity: 0.8,
  },
  button: {
    width: 120,
    height: 120,
    borderRadius: 60, // Perfect circle
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5, // Android shadow
  },
  buttonIdle: {
    backgroundColor: '#FFFFFF', // Blanco cuando está en reposo
    borderWidth: 2,
    borderColor: '#007AFF', // Borde azul
  },
  buttonRecording: {
    backgroundColor: '#007AFF', // Azul cuando está grabando
    width: 140, // Bigger when recording
    height: 140,
    borderRadius: 70, // Maintain circle shape
  },
  buttonText: {
    fontSize: 32,
    opacity: 0.8,
  },
});