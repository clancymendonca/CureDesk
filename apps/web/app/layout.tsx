import type { Metadata } from "next";
import { Work_Sans } from "next/font/google";
import "./globals.css";
import Providers from "./providers";

const workSans = Work_Sans({
  subsets: ["latin"],
  variable: "--font-work-sans",
});

export const metadata: Metadata = {
  title: "CureDesk",
  description:
    "CureDesk is a digital healthcare platform for symptom analysis, prescription scanning, and AI-assisted health guidance.",
  icons: {
    icon: "/logo-icon.png",
    shortcut: "/logo-icon.png",
    apple: "/logo-icon.png",
  },
  openGraph: {
    title: "CureDesk",
    description:
      "Digital healthcare with symptom analysis, prescription scanning, and AI-assisted health guidance.",
    images: [{ url: "/logo-icon.png", alt: "CureDesk" }],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="bg-cyan-500">
      <body className={workSans.variable}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
