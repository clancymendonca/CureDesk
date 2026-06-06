import { Link } from "expo-router";
import { View, Text, Pressable, StyleSheet } from "react-native";
import { theme, MEDICAL_DISCLAIMER } from "@curedesk/shared";

export default function HomeScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>CureDesk</Text>
      <Text style={styles.subtitle}>Your mobile health companion</Text>

      <Link href="/(tabs)/symptoms" asChild>
        <Pressable style={styles.button}>
          <Text style={styles.buttonText}>Check Symptoms</Text>
        </Pressable>
      </Link>
      <Link href="/(tabs)/prescription" asChild>
        <Pressable style={[styles.button, styles.buttonOutline]}>
          <Text style={[styles.buttonText, styles.buttonOutlineText]}>Scan Prescription</Text>
        </Pressable>
      </Link>
      <Link href="/(tabs)/chat" asChild>
        <Pressable style={[styles.button, styles.buttonOutline]}>
          <Text style={[styles.buttonText, styles.buttonOutlineText]}>Ask AI Assistant</Text>
        </Pressable>
      </Link>

      <Text style={styles.disclaimer}>{MEDICAL_DISCLAIMER}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, backgroundColor: theme.background, justifyContent: "center" },
  title: { fontSize: 32, fontWeight: "700", color: theme.secondary, marginBottom: 8 },
  subtitle: { fontSize: 16, color: theme.textMuted, marginBottom: 32 },
  button: {
    backgroundColor: theme.primary,
    paddingVertical: 16,
    borderRadius: 24,
    alignItems: "center",
    marginBottom: 12,
  },
  buttonOutline: { backgroundColor: "transparent", borderWidth: 2, borderColor: theme.primary },
  buttonText: { color: "#fff", fontSize: 16, fontWeight: "600" },
  buttonOutlineText: { color: theme.primary },
  disclaimer: { marginTop: 32, fontSize: 12, color: theme.textMuted, lineHeight: 18 },
});
