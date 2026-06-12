import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Prescription Analysis",
  description:
    "Scan a prescription image and identify medications with CureDesk's OCR-powered analysis.",
};

export default function PrescriptionLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
