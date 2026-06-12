import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Profile",
  description: "Your CureDesk account and recent activity.",
};

export default function ProfileLayout({ children }: { children: React.ReactNode }) {
  return children;
}
