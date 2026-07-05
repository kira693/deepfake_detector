import React from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity
} from 'react-native';

type VerdictKey = 'REAL' | 'AI_GENERATED' | 'DEEPFAKE' | 'INCONCLUSIVE';

const VERDICT_CONFIG: Record<VerdictKey, { color: string; bg: string; label: string; icon: string }> = {
  REAL:         { color: '#22c55e', bg: '#f0fdf4', label: 'Real',         icon: '✓' },
  AI_GENERATED: { color: '#f97316', bg: '#fff7ed', label: 'AI Generated', icon: '⚠' },
  DEEPFAKE:     { color: '#ef4444', bg: '#fef2f2', label: 'Deepfake',     icon: '✗' },
  INCONCLUSIVE: { color: '#8b5cf6', bg: '#f5f3ff', label: 'Inconclusive', icon: '?' },
};

export default function ResultScreen({ route, navigation }: any) {
  const { result } = route.params;
  const verdict: VerdictKey = result.result.verdict;
  const config = VERDICT_CONFIG[verdict] ?? VERDICT_CONFIG.INCONCLUSIVE;
  const confidence = Math.round(result.result.confidence * 100);
  const aiProb = Math.round(result.result.ai_probability * 100);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>

      <View style={[styles.verdictCard, { backgroundColor: config.bg, borderColor: config.color }]}>
        <Text style={[styles.verdictIcon, { color: config.color }]}>{config.icon}</Text>
        <Text style={[styles.verdictLabel, { color: config.color }]}>{config.label}</Text>
        <Text style={styles.filename} numberOfLines={1}>{result.filename}</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Confidence</Text>
        <View style={styles.barBg}>
          <View style={[styles.barFill, { width: `${confidence}%` as any, backgroundColor: config.color }]} />
        </View>
        <Text style={[styles.barLabel, { color: config.color }]}>{confidence}%</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>AI Probability</Text>
        <View style={styles.barBg}>
          <View style={[styles.barFill, { width: `${aiProb}%` as any, backgroundColor: '#6366f1' }]} />
        </View>
        <Text style={[styles.barLabel, { color: '#6366f1' }]}>{aiProb}%</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Details</Text>
        <DetailRow label="Detection type" value={result.result.detection_type} />
        <DetailRow label="Processing time" value={`${Math.round(result.result.processing_time_ms)}ms`} />
        <DetailRow label="File size" value={`${(result.file_size_bytes / 1024).toFixed(1)} KB`} />
        {result.faces_detected !== undefined && (
          <DetailRow label="Faces detected" value={String(result.faces_detected)} />
        )}
        {result.total_frames_analyzed !== undefined && (
          <DetailRow label="Frames analyzed" value={String(result.total_frames_analyzed)} />
        )}
      </View>

      <TouchableOpacity style={styles.primaryBtn} onPress={() => navigation.navigate('Home')}>
        <Text style={styles.primaryBtnText}>Analyze Another File</Text>
      </TouchableOpacity>

    </ScrollView>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.detailRow}>
      <Text style={styles.detailKey}>{label}</Text>
      <Text style={styles.detailValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  content: { padding: 24, paddingTop: 60 },
  verdictCard: {
    borderRadius: 16, padding: 28, alignItems: 'center',
    marginBottom: 16, borderWidth: 2,
  },
  verdictIcon: { fontSize: 48, fontWeight: 'bold', marginBottom: 8 },
  verdictLabel: { fontSize: 26, fontWeight: 'bold', marginBottom: 6 },
  filename: { fontSize: 13, color: '#888', marginTop: 4 },
  card: { backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 12 },
  cardTitle: { fontSize: 13, fontWeight: '600', color: '#888', marginBottom: 12, textTransform: 'uppercase' },
  barBg: { height: 10, backgroundColor: '#f0f0f0', borderRadius: 5, marginBottom: 6 },
  barFill: { height: 10, borderRadius: 5 },
  barLabel: { fontSize: 15, fontWeight: '700', textAlign: 'right' },
  detailRow: {
    flexDirection: 'row', justifyContent: 'space-between',
    paddingVertical: 8, borderBottomWidth: 0.5, borderBottomColor: '#f0f0f0',
  },
  detailKey: { fontSize: 14, color: '#666' },
  detailValue: { fontSize: 14, fontWeight: '600', color: '#1a1a1a' },
  primaryBtn: { backgroundColor: '#6366f1', borderRadius: 12, padding: 18, alignItems: 'center', marginTop: 8 },
  primaryBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
});