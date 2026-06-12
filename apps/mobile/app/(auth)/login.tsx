import { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  Pressable,
  StyleSheet,
  ActivityIndicator,
} from "react-native";
import { Link, router } from "expo-router";
import { theme } from "@curedesk/shared";
import {
  signInEmail,
  signUpEmail,
  useGoogleAuthRequest,
  signInWithGoogleIdToken,
} from "../../lib/firebase";

export default function LoginScreen() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSignUp, setIsSignUp] = useState(false);
  const [request, response, promptGoogle] = useGoogleAuthRequest();

  useEffect(() => {
    if (!response) return;
    if (response.type === "success") {
      const idToken = response.authentication?.idToken;
      if (idToken) {
        setLoading(true);
        signInWithGoogleIdToken(idToken)
          .then(() => router.back())
          .catch((e) => setError(e instanceof Error ? e.message : "Google sign-in failed"))
          .finally(() => setLoading(false));
      } else {
        setError("Google sign-in did not return a token. Please try again.");
      }
    } else if (response.type === "error") {
      setError(response.error?.message ?? "Google sign-in failed. Please try again.");
    } else if (response.type === "cancel" || response.type === "dismiss") {
      setError(null);
    }
  }, [response]);

  async function submit() {
    setLoading(true);
    setError(null);
    try {
      if (isSignUp) {
        await signUpEmail(email, password);
      } else {
        await signInEmail(email, password);
      }
      router.back();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Authentication failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{isSignUp ? "Create account" : "Sign in"}</Text>

      <Pressable
        style={[styles.button, styles.googleButton]}
        onPress={() => promptGoogle()}
        disabled={loading || !request}
      >
        <Text style={styles.googleButtonText}>Continue with Google</Text>
      </Pressable>

      <TextInput
        style={styles.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
      />
      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />

      {error && <Text style={styles.error}>{error}</Text>}

      <Pressable style={styles.button} onPress={submit} disabled={loading}>
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>{isSignUp ? "Sign Up" : "Sign In"}</Text>
        )}
      </Pressable>

      <Pressable onPress={() => setIsSignUp(!isSignUp)}>
        <Text style={styles.toggle}>
          {isSignUp ? "Already have an account? Sign in" : "Need an account? Sign up"}
        </Text>
      </Pressable>

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
  container: { flex: 1, padding: 24, justifyContent: "center", backgroundColor: theme.background },
  title: { fontSize: 24, fontWeight: "700", marginBottom: 24, color: theme.text },
  input: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    padding: 14,
    marginBottom: 12,
    backgroundColor: "#fff",
  },
  button: {
    backgroundColor: theme.primary,
    padding: 16,
    borderRadius: 24,
    alignItems: "center",
    marginTop: 8,
  },
  googleButton: {
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#ddd",
    marginBottom: 16,
  },
  buttonText: { color: "#fff", fontWeight: "600" },
  googleButtonText: { color: theme.text, fontWeight: "600" },
  error: { color: theme.error, marginBottom: 8 },
  toggle: { color: theme.primary, textAlign: "center", marginTop: 16 },
  link: { color: theme.textMuted, textAlign: "center", marginTop: 12, fontSize: 13 },
});
