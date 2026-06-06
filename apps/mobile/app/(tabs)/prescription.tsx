import { useState } from "react";
import {
  View,
  Text,
  Pressable,
  StyleSheet,
  ActivityIndicator,
  ScrollView,
  Image,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import { MEDICAL_DISCLAIMER, OCR_LOADING_MESSAGE, theme } from "@curedesk/shared";
import { api } from "../../lib/api";

export default function PrescriptionScreen() {
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [ocrText, setOcrText] = useState<string | null>(null);
  const [matches, setMatches] = useState<{ brand: string; generic: string; confidence: number }[]>(
    []
  );
  const [error, setError] = useState<string | null>(null);

  async function pickImage(useCamera: boolean) {
    const permission = useCamera
      ? await ImagePicker.requestCameraPermissionsAsync()
      : await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      setError("Permission required to access " + (useCamera ? "camera" : "photos"));
      return;
    }

    const result = useCamera
      ? await ImagePicker.launchCameraAsync({ quality: 0.8 })
      : await ImagePicker.launchImageLibraryAsync({ quality: 0.8 });

    if (result.canceled || !result.assets[0]) return;

    setPreview(result.assets[0].uri);
    setLoading(true);
    setError(null);
    setOcrText(null);
    setMatches([]);

    try {
      const blob = await fetch(result.assets[0].uri).then((r) => r.blob());
      const res = await api.scanPrescription(blob);
      setOcrText(res.ocr_text);
      setMatches(res.matches);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Scan failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.disclaimer}>{MEDICAL_DISCLAIMER}</Text>

      <Pressable style={styles.button} onPress={() => pickImage(true)}>
        <Text style={styles.buttonText}>Take Photo</Text>
      </Pressable>
      <Pressable style={[styles.button, styles.buttonOutline]} onPress={() => pickImage(false)}>
        <Text style={[styles.buttonText, styles.buttonOutlineText]}>Choose from Gallery</Text>
      </Pressable>

      {preview && <Image source={{ uri: preview }} style={styles.preview} />}

      {loading && (
        <View style={styles.loading}>
          <ActivityIndicator size="large" color={theme.primary} />
          <Text style={styles.loadingText}>{OCR_LOADING_MESSAGE}</Text>
        </View>
      )}

      {error && <Text style={styles.error}>{error}</Text>}

      {ocrText !== null && (
        <View style={styles.results}>
          <Text style={styles.resultsTitle}>OCR text</Text>
          <Text style={styles.ocrText}>{ocrText || "(no text detected)"}</Text>
          {matches.length > 0 && (
            <>
              <Text style={styles.resultsTitle}>Drug matches</Text>
              {matches.map((m) => (
                <Text key={m.brand} style={styles.matchItem}>
                  {m.brand} → {m.generic} ({(m.confidence * 100).toFixed(0)}%)
                </Text>
              ))}
            </>
          )}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.background },
  content: { padding: 16, paddingBottom: 40 },
  disclaimer: { fontSize: 12, color: theme.textMuted, marginBottom: 16, lineHeight: 18 },
  button: {
    backgroundColor: theme.primary,
    padding: 16,
    borderRadius: 24,
    alignItems: "center",
    marginBottom: 12,
  },
  buttonOutline: { backgroundColor: "transparent", borderWidth: 2, borderColor: theme.primary },
  buttonText: { color: "#fff", fontWeight: "600" },
  buttonOutlineText: { color: theme.primary },
  preview: { width: "100%", height: 200, borderRadius: 12, marginVertical: 16 },
  loading: { alignItems: "center", marginTop: 24 },
  loadingText: { marginTop: 12, color: theme.textMuted, textAlign: "center" },
  error: { color: theme.error, marginTop: 12 },
  results: { marginTop: 16, padding: 16, backgroundColor: "#fff", borderRadius: 12 },
  resultsTitle: { fontWeight: "700", marginTop: 12, marginBottom: 8 },
  ocrText: { fontSize: 14, color: theme.text },
  matchItem: { fontSize: 15, marginVertical: 4 },
});
