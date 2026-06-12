import { useEffect, useState } from "react";
import { useLocalSearchParams, Link } from "expo-router";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator } from "react-native";
import {
  DiseaseSummary,
  friendlyErrorMessage,
  humanizeSymptom,
  isNotFoundError,
  theme,
} from "@curedesk/shared";
import { api } from "../../lib/api";

export default function DiseaseDetailScreen() {
  const params = useLocalSearchParams<{ slug: string | string[] }>();
  const slug = Array.isArray(params.slug) ? params.slug[0] : params.slug;
  const [disease, setDisease] = useState<DiseaseSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (!slug) return;
    // Reset so navigating between diseases never shows stale content.
    setDisease(null);
    setError(null);
    setNotFound(false);
    let cancelled = false;
    api
      .getDisease(slug)
      .then((d) => {
        if (!cancelled) setDisease(d);
      })
      .catch((e) => {
        if (cancelled) return;
        if (isNotFoundError(e)) {
          setNotFound(true);
        } else {
          setError(friendlyErrorMessage(e, "Could not load this disease."));
        }
      });
    return () => {
      cancelled = true;
    };
  }, [slug]);

  if (notFound) {
    const name = humanizeSymptom(decodeURIComponent(slug ?? "").replace(/-/g, " "));
    return (
      <View style={[styles.container, styles.content]}>
        <Text style={styles.title}>{name || "Disease"}</Text>
        <Text style={styles.body}>
          We don&apos;t have a detailed page for this condition yet. Please consult a qualified
          healthcare professional for more information.
        </Text>
        <Link href="/(tabs)/symptoms" asChild>
          <Pressable><Text style={styles.link}>← Back to symptoms</Text></Pressable>
        </Link>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.error}>{error}</Text>
        <Link href="/(tabs)/symptoms" asChild>
          <Pressable><Text style={styles.link}>Back</Text></Pressable>
        </Link>
      </View>
    );
  }

  if (!disease) {
    return (
      <View style={styles.container}>
        <ActivityIndicator color={theme.primary} />
      </View>
    );
  }

  const symptoms = disease.common_symptoms as Record<string, number> | null;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Link href="/(tabs)/symptoms" asChild>
        <Pressable><Text style={styles.link}>← Back</Text></Pressable>
      </Link>
      <Text style={styles.title}>{disease.name}</Text>
      {disease.description && <Text style={styles.body}>{disease.description}</Text>}
      {symptoms && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Common symptom rates</Text>
          {Object.entries(symptoms).map(([key, val]) => (
            <View key={key} style={styles.row}>
              <Text style={styles.rowLabel}>{key.replace(/_/g, " ")}</Text>
              <Text>{(val * 100).toFixed(0)}%</Text>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.background },
  content: { padding: 16, paddingBottom: 40 },
  title: { fontSize: 24, fontWeight: "700", color: theme.text, marginVertical: 12 },
  body: { color: theme.textMuted, marginBottom: 16, lineHeight: 22 },
  card: { backgroundColor: "#fff", padding: 16, borderRadius: 12 },
  cardTitle: { fontWeight: "700", marginBottom: 12 },
  row: { flexDirection: "row", justifyContent: "space-between", marginVertical: 4 },
  rowLabel: { textTransform: "capitalize" },
  link: { color: theme.primary, marginBottom: 8 },
  error: { color: theme.error },
});
