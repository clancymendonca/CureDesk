import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Symptom Analysis",
  description:
    "Check your symptoms and get AI-assisted disease predictions with CureDesk.",
};

export default function SymptomAnalysisLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
