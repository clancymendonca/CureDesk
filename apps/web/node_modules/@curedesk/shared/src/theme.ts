export const theme = {
  primary: "#344CB7",
  secondary: "#000957",
  accent: "#06b6d4",
  accentDark: "#0e7490",
  background: "#F7F7F7",
  text: "#141413",
  textMuted: "#7D8087",
  white: "#FFFFFF",
  error: "#dc2626",
  success: "#16a34a",
} as const;

export type Theme = typeof theme;
