import { useState } from "react";
import {
  View,
  Text,
  TextInput,
  Pressable,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
} from "react-native";
import { MEDICAL_DISCLAIMER, theme } from "@curedesk/shared";
import { api } from "../../lib/api";

export default function ChatScreen() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<{ role: "user" | "assistant"; content: string }[]>([]);
  const [loading, setLoading] = useState(false);

  async function send() {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    const history = [...messages, { role: "user" as const, content: userMsg }];
    setMessages(history);
    setLoading(true);
    try {
      const res = await api.chat({ message: userMsg, history: messages });
      setMessages([...history, { role: "assistant", content: res.reply }]);
    } catch {
      setMessages([...history, { role: "assistant", content: "Sorry, chat is unavailable right now." }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.disclaimer}>{MEDICAL_DISCLAIMER}</Text>
      <ScrollView style={styles.messages} contentContainerStyle={styles.messagesContent}>
        {messages.map((m, i) => (
          <View
            key={i}
            style={[styles.bubble, m.role === "user" ? styles.userBubble : styles.aiBubble]}
          >
            <Text style={m.role === "user" ? styles.userText : styles.aiText}>{m.content}</Text>
          </View>
        ))}
        {loading && <ActivityIndicator style={{ marginTop: 8 }} color={theme.primary} />}
      </ScrollView>
      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          value={input}
          onChangeText={setInput}
          placeholder="Ask a health question..."
          multiline
        />
        <Pressable style={styles.send} onPress={send} disabled={loading}>
          <Text style={styles.sendText}>Send</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.background },
  disclaimer: { fontSize: 11, color: theme.textMuted, padding: 12, lineHeight: 16 },
  messages: { flex: 1 },
  messagesContent: { padding: 12 },
  bubble: { padding: 12, borderRadius: 12, marginBottom: 8, maxWidth: "85%" },
  userBubble: { backgroundColor: theme.primary, alignSelf: "flex-end" },
  aiBubble: { backgroundColor: "#fff", alignSelf: "flex-start" },
  userText: { color: "#fff" },
  aiText: { color: theme.text },
  inputRow: { flexDirection: "row", padding: 12, gap: 8, borderTopWidth: 1, borderColor: "#eee" },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    backgroundColor: "#fff",
    maxHeight: 100,
  },
  send: {
    backgroundColor: theme.primary,
    borderRadius: 20,
    paddingHorizontal: 20,
    justifyContent: "center",
  },
  sendText: { color: "#fff", fontWeight: "600" },
});
