import React, { useState } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet,
  ActivityIndicator, Alert, ScrollView
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { detectImage, detectDeepfake, detectVideo } from '../services/api';

const DETECTION_TYPES = [
  { key: 'image',    label: 'AI Image',  emoji: '🖼️', desc: 'Detect AI-generated images' },
  { key: 'deepfake', label: 'Deepfake',  emoji: '👤', desc: 'Detect deepfake faces' },
  { key: 'video',    label: 'AI Video',  emoji: '🎬', desc: 'Detect AI-generated videos' },
];

export default function HomeScreen({ navigation }: any) {
  const [selectedType, setSelectedType] = useState('image');
  const [loading, setLoading] = useState(false);

  const pickAndAnalyze = async () => {
    try {
      const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (!permission.granted) {
        Alert.alert('Permission needed', 'Please allow access to your media library.');
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
       mediaTypes: ['images'],
         
        quality: 1,
      });

      if (result.canceled) return;

      const asset = result.assets[0];
      setLoading(true);

      let response;
      const filename = asset.uri.split('/').pop() || 'file.jpg';

      if (selectedType === 'image') {
        response = await detectImage(asset.uri, filename);
      } else if (selectedType === 'deepfake') {
        response = await detectDeepfake(asset.uri, filename);
      } else {
        response = await detectVideo(asset.uri, filename);
      }

      navigation.navigate('Result', { result: JSON.stringify(response) });
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Could not connect to server.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>DeepFake Detector</Text>
      <Text style={styles.subtitle}>Select detection type then upload a file</Text>

      <Text style={styles.sectionLabel}>Detection Type</Text>
      {DETECTION_TYPES.map((type) => (
        <TouchableOpacity
          key={type.key}
          style={[styles.typeCard, selectedType === type.key && styles.typeCardSelected]}
          onPress={() => setSelectedType(type.key)}
        >
          <Text style={styles.typeEmoji}>{type.emoji}</Text>
          <View>
            <Text style={[styles.typeLabel, selectedType === type.key && styles.typeLabelSelected]}>
              {type.label}
            </Text>
            <Text style={styles.typeDesc}>{type.desc}</Text>
          </View>
          {selectedType === type.key && <Text style={styles.check}>✓</Text>}
        </TouchableOpacity>
      ))}

      <TouchableOpacity
        style={[styles.uploadBtn, loading && styles.uploadBtnDisabled]}
        onPress={pickAndAnalyze}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.uploadBtnText}>
            {selectedType === 'video' ? 'Pick Video & Analyze' : 'Pick Image & Analyze'}
          </Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  content: { padding: 24, paddingTop: 60 },
  title: { fontSize: 28, fontWeight: 'bold', color: '#1a1a1a', marginBottom: 6 },
  subtitle: { fontSize: 15, color: '#666', marginBottom: 32 },
  sectionLabel: { fontSize: 13, fontWeight: '600', color: '#888', marginBottom: 12, textTransform: 'uppercase' },
  typeCard: {
    flexDirection: 'row', alignItems: 'center', gap: 14,
    backgroundColor: '#fff', borderRadius: 12, padding: 16,
    marginBottom: 10, borderWidth: 2, borderColor: 'transparent',
  },
  typeCardSelected: { borderColor: '#6366f1', backgroundColor: '#eef2ff' },
  typeEmoji: { fontSize: 28 },
  typeLabel: { fontSize: 16, fontWeight: '600', color: '#1a1a1a' },
  typeLabelSelected: { color: '#6366f1' },
  typeDesc: { fontSize: 13, color: '#888', marginTop: 2 },
  check: { marginLeft: 'auto', color: '#6366f1', fontSize: 18, fontWeight: 'bold' },
  uploadBtn: {
    backgroundColor: '#6366f1', borderRadius: 12,
    padding: 18, alignItems: 'center', marginTop: 24,
  },
  uploadBtnDisabled: { backgroundColor: '#a5b4fc' },
  uploadBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
});