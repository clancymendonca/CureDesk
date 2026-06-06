import { ScrollView, Text, StyleSheet } from "react-native";
import { theme } from "@curedesk/shared";

export default function PrivacyScreen() {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Privacy Policy</Text>
      <Text style={styles.body}>
        CureDesk collects symptom submissions and prescription scans you choose to submit.
        Authenticated users may have activity linked to their Firebase account. We do not sell
        personal health data. Contact us to request deletion of your account data.
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
