import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Log In",
  description: "Sign in to CureDesk to save your activity and access your profile.",
};

export default function LoginLayout({ children }: { children: React.ReactNode }) {
  return children;
}
