import { useEffect, useState } from "react";
import { View, Text, Pressable, StyleSheet, ActivityIndicator } from "react-native";
import { Link } from "expo-router";
import { friendlyErrorMessage, theme, type HistoryItem } from "@curedesk/shared";
import { useAuth } from "../../lib/auth-context";
import { signOut } from "../../lib/firebase";
import { api } from "../../lib/api";

export default function ProfileScreen() {
  const { user, loading: authLoading } = useAuth();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [signOutError, setSignOutError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    setHistoryError(null);
    api
      .profileHistory()
      .then((res) => setHistory(res.items))
      .catch((e) => {
        setHistory([]);
        setHistoryError(friendlyErrorMessage(e, "Couldn't load your history."));
      })
      .finally(() => setLoading(false));
  }, [user]);

  async function handleSignOut() {
    try {
      setSignOutError(null);
      await signOut();
    } catch {
      setSignOutError("Sign out failed. Please try again.");
    }
  }

  if (authLoading) {
    return (
      <View style={[styles.container, styles.centered]}>
        <ActivityIndicator color={theme.primary} />
      </View>
    );
  }

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

      <Pressable style={styles.buttonOutline} onPress={handleSignOut}>
        <Text style={styles.buttonOutlineText}>Sign Out</Text>
      </Pressable>
      {signOutError && <Text style={styles.error}>{signOutError}</Text>}

      <Text style={styles.sectionTitle}>Recent activity</Text>
      {loading ? (
        <ActivityIndicator color={theme.primary} />
      ) : historyError ? (
        <Text style={styles.error}>{historyError}</Text>
      ) : history.length === 0 ? (
        <Text style={styles.empty}>No history yet</Text>
      ) : (
        history.map((h) => (
          <Text key={h.id} style={styles.historyItem}>
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
  centered: { justifyContent: "center", alignItems: "center" },
  error: { color: theme.error, marginBottom: 12 },
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
