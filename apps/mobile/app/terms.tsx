import { ScrollView, Text, StyleSheet } from "react-native";
import { theme } from "@curedesk/shared";

export default function TermsScreen() {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Terms of Service</Text>
      <Text style={styles.body}>
        CureDesk provides informational health content only. By using this app you agree that
        CureDesk is not a medical provider and does not offer diagnosis or treatment. Always
        consult a qualified healthcare professional for medical decisions.
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.background },
  content: { padding: 24 },
  title: { fontSize: 22, fontWeight: "700", marginBottom: 16 },
  body: { fontSize: 15, lineHeight: 24, color: theme.text },
});
