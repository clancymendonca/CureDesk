"use client";

import { useEffect, useState } from "react";
import {
  SYMPTOM_FEATURES,
  advancedSymptomFeatures,
  humanizeSymptom,
} from "@curedesk/shared";
import { api } from "@/lib/api";

type Props = {
  values: Record<string, boolean>;
  onChange: (values: Record<string, boolean>) => void;
};

export function AdvancedSymptomsPanel({ values, onChange }: Props) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [allFeatures, setAllFeatures] = useState<readonly string[]>(SYMPTOM_FEATURES);

  useEffect(() => {
    let cancelled = false;
    api
      .getSymptomFeatures()
      .then((r) => {
        if (!cancelled && r.features.length) setAllFeatures(r.features);
      })
      .catch(() => {
        /* keep bundled fallback list */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const features = advancedSymptomFeatures(search, allFeatures);
  const selectedCount = Object.values(values).filter(Boolean).length;

  function toggle(key: string, checked: boolean) {
    onChange({ ...values, [key]: checked });
  }

  return (
    <div className="border rounded-lg p-4 bg-gray-50">
      <button
        type="button"
        className="w-full flex justify-between items-center text-left font-semibold text-teal-900"
        onClick={() => setOpen(!open)}
      >
        <span>Advanced symptoms ({selectedCount} selected)</span>
        <span>{open ? "−" : "+"}</span>
      </button>
      {open && (
        <div className="mt-3 space-y-3">
          <input
            type="search"
            placeholder="Search symptoms..."
            className="w-full border rounded-lg px-3 py-2 text-sm bg-white"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <div className="max-h-64 overflow-y-auto grid grid-cols-1 sm:grid-cols-2 gap-2 pr-1">
            {features.map((key) => (
              <label key={key} className="flex items-start gap-2 text-sm">
                <input
                  type="checkbox"
                  className="mt-0.5"
                  checked={!!values[key]}
                  onChange={(e) => toggle(key, e.target.checked)}
                />
                <span>{humanizeSymptom(key)}</span>
              </label>
            ))}
          </div>
          {features.length === 0 && (
            <p className="text-sm text-gray-500">No symptoms match your search.</p>
          )}
        </div>
      )}
    </div>
  );
}
