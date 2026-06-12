"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  DiseaseSummary,
  friendlyErrorMessage,
  humanizeSymptom,
  isNotFoundError,
} from "@curedesk/shared";
import { api } from "@/lib/api";
import PageLayout from "@/components/PageLayout";

export default function DiseaseDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const [disease, setDisease] = useState<DiseaseSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (!slug) return;
    api
      .getDisease(slug)
      .then(setDisease)
      .catch((e) => {
        if (isNotFoundError(e)) {
          setNotFound(true);
        } else {
          setError(friendlyErrorMessage(e, "Could not load this disease."));
        }
      });
  }, [slug]);

  if (notFound) {
    const name = humanizeSymptom(decodeURIComponent(slug ?? "").replace(/-/g, " "));
    return (
      <PageLayout title={name || "Disease"}>
        <div className="page-card space-y-4">
          <p className="text-16-medium">
            We don&apos;t have a detailed page for {name || "this condition"} yet. Please consult a
            qualified healthcare professional for more information.
          </p>
          <Link href="/symptom-analysis" className="text-primary inline-block hover:underline">
            ← Back to symptoms
          </Link>
        </div>
      </PageLayout>
    );
  }

  if (error) {
    return (
      <PageLayout title="Disease">
        <div className="page-card">
          <p className="startup-form_error">{error}</p>
          <Link href="/symptom-analysis" className="text-primary mt-4 inline-block hover:underline">
            Back to symptoms
          </Link>
        </div>
      </PageLayout>
    );
  }

  if (!disease) {
    return (
      <PageLayout title="Disease">
        <div className="page-card">
          <p className="text-16-medium">Loading...</p>
        </div>
      </PageLayout>
    );
  }

  const symptoms = disease.common_symptoms as Record<string, number> | null;

  return (
    <PageLayout title={disease.name}>
      <div className="page-card space-y-6">
        <Link
          href="/symptom-analysis"
          className="text-primary text-sm inline-block hover:underline"
        >
          ← Back to symptoms
        </Link>

        {disease.description && (
          <div>
            <h2 className="page-card-title">Overview</h2>
            <p className="startup-card_desc !line-clamp-none">{disease.description}</p>
          </div>
        )}

        {symptoms && (
          <div>
            <h2 className="page-card-title">Common symptom rates</h2>
            <ul className="space-y-2">
              {Object.entries(symptoms).map(([key, val]) => (
                <li key={key} className="flex justify-between capitalize text-16-medium border-b-[2px] border-black/10 pb-2 last:border-0">
                  <span>{key.replace(/_/g, " ")}</span>
                  <span>{(val * 100).toFixed(0)}%</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </PageLayout>
  );
}
