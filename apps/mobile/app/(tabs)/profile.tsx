import { useEffect, useState } from "react";
import { View, Text, Pressable, StyleSheet, ActivityIndicator } from "react-native";
import { Link } from "expo-router";
import { theme } from "@curedesk/shared";
import { useAuth } from "../../lib/auth-context";
import { signOut } from "../../lib/firebase";
import { api } from "../../lib/api";

export default function ProfileScreen() {
  const user = useAuth();
  const [history, setHistory] = useState<{ summary: string; created_at: string }[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    api
      .profileHistory()
      .then((res) => setHistory(res.items))
      .catch(() => setHistory([]))
      .finally(() => setLoading(false));
  }, [user]);

  if (!user) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>Sign in to save history</Text>
        <Link href="/(auth)/login" asChild>
          <Pressable style={styles.button}>
            <Text style={styles.buttonText}>Sign In</Text>
          </Pressable>
        </Link>
        <Link href="/terms" asChild>
          <Text style={styles.link}>Terms of Service</Text>
        </Link>
        <Link href="/privacy" asChild>
          <Text style={styles.link}>Privacy Policy</Text>
        </Link>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{user.displayName ?? user.email}</Text>
      <Text style={styles.email}>{user.email}</Text>

      <Pressable style={styles.buttonOutline} onPress={() => signOut()}>
        <Text style={styles.buttonOutlineText}>Sign Out</Text>
      </Pressable>

      <Text style={styles.sectionTitle}>Recent activity</Text>
      {loading ? (
        <ActivityIndicator color={theme.primary} />
      ) : history.length === 0 ? (
        <Text style={styles.empty}>No history yet</Text>
      ) : (
        history.map((h, i) => (
          <Text key={i} style={styles.historyItem}>
            {h.summary}
          </Text>
        ))
      )}

      <Link href="/terms" asChild>
        <Text style={styles.link}>Terms of Service</Text>
      </Link>
      <Link href="/privacy" asChild>
        <Text style={styles.link}>Privacy Policy</Text>
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, backgroundColor: theme.background },
  title: { fontSize: 22, fontWeight: "700", color: theme.text },
  email: { color: theme.textMuted, marginBottom: 24 },
  button: {
    backgroundColor: theme.primary,
    padding: 16,
    borderRadius: 24,
    alignItems: "center",
    marginBottom: 16,
  },
  buttonText: { color: "#fff", fontWeight: "600" },
  buttonOutline: {
    borderWidth: 2,
    borderColor: theme.primary,
    padding: 12,
    borderRadius: 24,
    alignItems: "center",
    marginBottom: 24,
  },
  buttonOutlineText: { color: theme.primary, fontWeight: "600" },
  sectionTitle: { fontWeight: "700", marginBottom: 12 },
  historyItem: { fontSize: 14, marginBottom: 8, color: theme.text },
  empty: { color: theme.textMuted },
  link: { color: theme.primary, marginTop: 16, fontSize: 14 },
});
