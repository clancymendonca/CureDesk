import type { Metadata } from "next";
import Link from "next/link";
import LegalPageLayout, { type LegalSection } from "@/components/LegalPageLayout";

export const metadata: Metadata = {
  title: "Privacy Policy | CureDesk",
  description: "How CureDesk collects, uses, and protects your information.",
};

const LAST_UPDATED = "June 6, 2026";

const sections: LegalSection[] = [
  {
    id: "overview",
    title: "Overview",
    content: (
      <>
        <p>
          CureDesk is committed to handling your information responsibly. This Privacy Policy
          explains what data we collect when you use our platform, why we collect it, and the
          choices you have.
        </p>
        <p>
          By using CureDesk, you acknowledge the practices described here. If you do not agree,
          please discontinue use of the service.
        </p>
      </>
    ),
  },
  {
    id: "information-we-collect",
    title: "Information we collect",
    content: (
      <>
        <p>Depending on how you use CureDesk, we may collect:</p>
        <ul>
          <li>
            <strong>Account information</strong> — such as your email address, display name, and
            Firebase authentication identifiers when you sign up or log in.
          </li>
          <li>
            <strong>Symptom and health inputs</strong> — symptoms, age, gender, and related
            health details you submit for analysis.
          </li>
          <li>
            <strong>Prescription uploads</strong> — images you choose to scan and the text
            extracted from them through OCR.
          </li>
          <li>
            <strong>Chat messages</strong> — questions you send to the AI assistant and the
            responses generated for you.
          </li>
          <li>
            <strong>Usage and activity history</strong> — summaries of recent interactions linked
            to your account when you are signed in.
          </li>
          <li>
            <strong>Technical data</strong> — basic device, browser, and request information
            needed to operate and secure the service.
          </li>
        </ul>
        <p>
          We only collect health-related information that you voluntarily provide. You can use
          some features without creating an account, though certain history and profile features
          require authentication.
        </p>
      </>
    ),
  },
  {
    id: "how-we-use",
    title: "How we use information",
    content: (
      <>
        <p>We use collected information to:</p>
        <ul>
          <li>Provide symptom analysis, prescription scanning, chat, and disease information features.</li>
          <li>Maintain your account and show activity history when you are logged in.</li>
          <li>Improve reliability, accuracy, and security of the platform.</li>
          <li>Respond to support requests and enforce our Terms of Service.</li>
        </ul>
        <p>
          We do not use your personal health information for advertising profiling, and we do not
          sell personal health data to third parties.
        </p>
      </>
    ),
  },
  {
    id: "authentication",
    title: "Authentication and third-party services",
    content: (
      <>
        <p>
          CureDesk uses Firebase Authentication to manage sign-in and account security. Firebase
          processes account credentials according to Google&apos;s privacy and security practices.
        </p>
        <p>
          Our backend API processes the health inputs and files you submit in order to return
          predictions, extracted prescription text, chat replies, and related results. These
          services are operated to support CureDesk functionality, not for unrelated commercial
          purposes.
        </p>
      </>
    ),
  },
  {
    id: "storage-security",
    title: "Storage and security",
    content: (
      <>
        <p>
          We take reasonable technical and organizational measures to protect your information
          against unauthorized access, loss, or misuse. No method of transmission or storage is
          completely secure, and we cannot guarantee absolute security.
        </p>
        <p>
          We retain information only as long as needed to provide the service, comply with legal
          obligations, resolve disputes, and enforce our agreements.
        </p>
      </>
    ),
  },
  {
    id: "sharing",
    title: "When we share information",
    content: (
      <>
        <p>We do not sell your personal or health information. We may share data only:</p>
        <ul>
          <li>With service providers that help us operate CureDesk, under confidentiality obligations.</li>
          <li>When required by law, regulation, legal process, or governmental request.</li>
          <li>To protect the rights, safety, and security of CureDesk, our users, or the public.</li>
          <li>With your consent or at your direction.</li>
        </ul>
      </>
    ),
  },
  {
    id: "your-choices",
    title: "Your choices and rights",
    content: (
      <>
        <p>You can control your information in several ways:</p>
        <ul>
          <li>Review recent activity from your profile when signed in.</li>
          <li>Choose not to create an account, understanding that some features may be limited.</li>
          <li>Request account deletion or correction of inaccurate account information by contacting us.</li>
          <li>Stop using CureDesk at any time.</li>
        </ul>
        <p>
          Depending on where you live, you may have additional privacy rights under local law. We
          will honor valid requests to the extent we are legally required to do so.
        </p>
      </>
    ),
  },
  {
    id: "cookies",
    title: "Cookies and local storage",
    content: (
      <>
        <p>
          CureDesk may use cookies, local storage, or similar technologies to keep you signed in,
          remember preferences, and maintain session security. You can adjust browser settings to
          limit cookies, though some features may not work correctly if essential cookies are
          disabled.
        </p>
      </>
    ),
  },
  {
    id: "children",
    title: "Children's privacy",
    content: (
      <>
        <p>
          CureDesk is not directed at children under 13, and we do not knowingly collect personal
          information from children under 13. If you believe a child has provided us with personal
          information, please contact us so we can take appropriate action.
        </p>
      </>
    ),
  },
  {
    id: "changes",
    title: "Changes to this policy",
    content: (
      <>
        <p>
          We may update this Privacy Policy from time to time. The &quot;Last updated&quot; date
          at the top of this page reflects the latest revision. Material changes may be communicated
          through the platform or by email where appropriate.
        </p>
      </>
    ),
  },
  {
    id: "contact",
    title: "Contact",
    content: (
      <>
        <p>
          For privacy questions, data access requests, or deletion requests, contact the CureDesk
          project maintainers through the channels provided on the website.
        </p>
        <p>
          For terms of use, see our{" "}
          <Link href="/terms" className="text-primary font-medium hover:underline">
            Terms of Service
          </Link>
          .
        </p>
      </>
    ),
  },
];

export default function PrivacyPage() {
  return (
    <LegalPageLayout
      title="Privacy Policy"
      subtitle="How CureDesk handles the information you share with us."
      lastUpdated={LAST_UPDATED}
      sections={sections}
      relatedLink={{ href: "/terms", label: "Terms of Service" }}
    />
  );
}
