"use client";

import { useState } from "react";
import { MEDICAL_DISCLAIMER, OCR_LOADING_MESSAGE, friendlyErrorMessage } from "@curedesk/shared";
import { api } from "@/lib/api";
import PageLayout from "@/components/PageLayout";

export default function PrescriptionPage() {
  const [loading, setLoading] = useState(false);
  const [ocrText, setOcrText] = useState<string | null>(null);
  const [matches, setMatches] = useState<{ brand: string; generic: string; confidence: number }[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setError(null);
    setOcrText(null);
    setMatches([]);
    try {
      const res = await api.scanPrescription(file);
      setOcrText(res.ocr_text);
      setMatches(res.matches);
    } catch (err) {
      setError(friendlyErrorMessage(err, "Scan failed. Please try again."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <PageLayout title="Prescription Analysis" subtitle={MEDICAL_DISCLAIMER}>
      <div className="space-y-8">
        <div className="page-card startup-form !my-0 max-w-none w-full">
          <label className="startup-form_label">Upload prescription image</label>
          <input
            type="file"
            accept="image/jpeg,image/jpg,image/png"
            onChange={onFile}
            disabled={loading}
            className="startup-form_input w-full"
          />
          {loading && (
            <p className="text-16-medium mt-4 flex items-center gap-2">
              <span className="animate-spin inline-block w-4 h-4 border-2 border-primary border-t-transparent rounded-full" />
              {OCR_LOADING_MESSAGE}
            </p>
          )}
        </div>

        {error && <p className="startup-form_error">{error}</p>}

        {ocrText !== null && (
          <div className="page-card space-y-6">
            <div>
              <h2 className="page-card-title">OCR text</h2>
              <p className="startup-card_desc">{ocrText || "(no text detected)"}</p>
            </div>
            {matches.length > 0 && (
              <div>
                <h2 className="page-card-title !mt-6">Drug matches</h2>
                <ul className="space-y-2">
                  {matches.map((m, i) => (
                    <li key={`${m.brand}-${m.generic}-${i}`} className="text-16-medium">
                      {m.brand} → {m.generic} ({(m.confidence * 100).toFixed(0)}%)
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </PageLayout>
  );
}
