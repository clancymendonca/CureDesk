import type { Metadata } from "next";
import { MEDICAL_DISCLAIMER } from "@curedesk/shared";
import LegalPageLayout, { type LegalSection } from "@/components/LegalPageLayout";

export const metadata: Metadata = {
  title: "Terms of Service | CureDesk",
  description: "Terms of Service for the CureDesk digital healthcare platform.",
};

const LAST_UPDATED = "June 6, 2026";

const sections: LegalSection[] = [
  {
    id: "acceptance",
    title: "Acceptance of terms",
    content: (
      <>
        <p>
          By accessing or using CureDesk — including our website, symptom analysis tools,
          prescription scanning, AI chat assistant, and related services — you agree to these Terms
          of Service. If you do not agree, please do not use the platform.
        </p>
        <p>
          These terms apply to all visitors, registered users, and anyone who interacts with
          CureDesk on the web or through connected applications.
        </p>
      </>
    ),
  },
  {
    id: "not-medical-advice",
    title: "Not medical advice",
    content: (
      <>
        <p>{MEDICAL_DISCLAIMER}</p>
        <p>
          CureDesk is an informational and educational tool. We are not a licensed medical
          provider, hospital, or pharmacy. Nothing on CureDesk — including symptom predictions,
          disease summaries, prescription text extraction, or chatbot responses — constitutes a
          diagnosis, treatment plan, or prescription.
        </p>
        <p>
          If you think you may have a medical emergency, call your local emergency number
          immediately. Do not rely on CureDesk for urgent or life-threatening situations.
        </p>
      </>
    ),
  },
  {
    id: "eligibility",
    title: "Eligibility",
    content: (
      <>
        <p>
          You must be at least 18 years old to create an account. If you are under 18, you may
          only use CureDesk with the involvement and consent of a parent or legal guardian.
        </p>
        <p>
          You represent that the information you provide is accurate to the best of your knowledge
          and that you will use the service only for lawful, personal, non-commercial purposes
          unless we agree otherwise in writing.
        </p>
      </>
    ),
  },
  {
    id: "accounts",
    title: "Accounts and authentication",
    content: (
      <>
        <p>
          Some features require a CureDesk account. Authentication is handled through Firebase.
          You are responsible for keeping your login credentials secure and for all activity that
          occurs under your account.
        </p>
        <ul>
          <li>Notify us promptly if you suspect unauthorized access to your account.</li>
          <li>Do not share your account or impersonate another person.</li>
          <li>We may suspend or terminate accounts that violate these terms or pose a security risk.</li>
        </ul>
      </>
    ),
  },
  {
    id: "services",
    title: "Our services",
    content: (
      <>
        <p>CureDesk may offer the following features, which can change over time:</p>
        <ul>
          <li>
            <strong>Symptom analysis</strong> — probabilistic suggestions based on symptoms and
            health inputs you provide. Results are estimates, not clinical conclusions.
          </li>
          <li>
            <strong>Prescription scanning</strong> — optical character recognition (OCR) to extract
            text from uploaded prescription images. Always verify extracted information with your
            pharmacist or prescriber.
          </li>
          <li>
            <strong>AI chat assistant</strong> — general health information drawn from indexed
            medical content. Responses may be incomplete or outdated.
          </li>
          <li>
            <strong>Disease information</strong> — educational summaries intended to help you
            learn about conditions, not to replace professional evaluation.
          </li>
        </ul>
        <p>
          We do not guarantee the accuracy, completeness, or availability of any feature. Services
          may be modified, limited, or discontinued at any time.
        </p>
      </>
    ),
  },
  {
    id: "responsibilities",
    title: "Your responsibilities",
    content: (
      <>
        <p>When using CureDesk, you agree not to:</p>
        <ul>
          <li>Submit false, misleading, or another person&apos;s health information without consent.</li>
          <li>Upload unlawful, harmful, or unrelated content through prescription or chat features.</li>
          <li>Attempt to reverse engineer, scrape, overload, or disrupt our systems.</li>
          <li>Use CureDesk to provide medical care to others on a professional basis without proper licensing.</li>
        </ul>
        <p>
          You remain solely responsible for decisions you make based on information from CureDesk.
        </p>
      </>
    ),
  },
  {
    id: "intellectual-property",
    title: "Intellectual property",
    content: (
      <>
        <p>
          CureDesk, its branding, software, design, and original content are owned by CureDesk or
          its licensors and are protected by applicable intellectual property laws.
        </p>
        <p>
          You may use the platform for personal purposes as intended. You may not copy, modify,
          distribute, or create derivative works from our materials without prior written
          permission.
        </p>
      </>
    ),
  },
  {
    id: "liability",
    title: "Limitation of liability",
    content: (
      <>
        <p>
          To the fullest extent permitted by law, CureDesk and its contributors are not liable for
          any indirect, incidental, special, consequential, or punitive damages arising from your
          use of the platform.
        </p>
        <p>
          CureDesk is provided on an &quot;as is&quot; and &quot;as available&quot; basis without
          warranties of any kind, whether express or implied, including fitness for a particular
          purpose or non-infringement.
        </p>
      </>
    ),
  },
  {
    id: "changes",
    title: "Changes to these terms",
    content: (
      <>
        <p>
          We may update these Terms of Service from time to time. When we do, we will revise the
          &quot;Last updated&quot; date at the top of this page. Continued use of CureDesk after
          changes take effect constitutes acceptance of the updated terms.
        </p>
        <p>
          For material changes, we may also provide notice through the app or by email where
          appropriate.
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
          Questions about these terms can be directed through the contact options listed on the
          CureDesk website or by reaching out to the project maintainers.
        </p>
        <p>
          For privacy-related requests, please see our{" "}
          <a href="/privacy" className="text-primary font-medium hover:underline">
            Privacy Policy
          </a>
          .
        </p>
      </>
    ),
  },
];

export default function TermsPage() {
  return (
    <LegalPageLayout
      title="Terms of Service"
      subtitle="Please read these terms carefully before using CureDesk."
      lastUpdated={LAST_UPDATED}
      sections={sections}
      relatedLink={{ href: "/privacy", label: "Privacy Policy" }}
    />
  );
}
