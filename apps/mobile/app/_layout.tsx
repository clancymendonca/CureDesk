import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import * as Sentry from "@sentry/react-native";
import { AuthProvider } from "../lib/auth-context";

const dsn = process.env.EXPO_PUBLIC_SENTRY_DSN;
if (dsn) {
  Sentry.init({
    dsn,
    tracesSampleRate: 0.1,
    beforeSend(event) {
      if (event.extra) {
        delete event.extra.symptoms;
        delete event.extra.ocr_text;
      }
      return event;
    },
  });
}

const queryClient = new QueryClient();

export default function RootLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <StatusBar style="dark" />
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="(tabs)" />
          <Stack.Screen name="(auth)/login" options={{ presentation: "modal" }} />
          <Stack.Screen name="disease/[slug]" options={{ title: "Disease" }} />
          <Stack.Screen name="terms" options={{ title: "Terms" }} />
          <Stack.Screen name="privacy" options={{ title: "Privacy" }} />
        </Stack>
      </AuthProvider>
    </QueryClientProvider>
  );
}
