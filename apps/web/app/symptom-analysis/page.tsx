"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  MEDICAL_DISCLAIMER,
  DiseaseSummary,
  buildSymptomsPayload,
  friendlyErrorMessage,
} from "@curedesk/shared";
import { api } from "@/lib/api";
import PageLayout from "@/components/PageLayout";
import { AdvancedSymptomsPanel } from "@/components/AdvancedSymptomsPanel";
import { Button } from "@/components/ui/button";

export default function SymptomAnalysisPage() {
  const [fever, setFever] = useState(false);
  const [cough, setCough] = useState(false);
  const [fatigue, setFatigue] = useState(false);
  const [difficultyBreathing, setDifficultyBreathing] = useState(false);
  const [advancedSymptoms, setAdvancedSymptoms] = useState<Record<string, boolean>>({});
  const [age, setAge] = useState(30);
  const [gender, setGender] = useState<"male" | "female">("female");
  const [bloodPressure, setBloodPressure] = useState<"normal" | "high" | "low">("normal");
  const [cholesterol, setCholesterol] = useState<"normal" | "high">("normal");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<{ disease: string; slug: string; probability: number }[] | null>(null);
  const [confidenceLevel, setConfidenceLevel] = useState<"high" | "medium" | "low" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [diseases, setDiseases] = useState<DiseaseSummary[]>([]);
  const [diseasesError, setDiseasesError] = useState<string | null>(null);

  useEffect(() => {
    const t = setTimeout(() => {
      api
        .listDiseases(search || undefined)
        .then((r) => {
          setDiseases(r.items);
          setDiseasesError(null);
        })
        .catch((err) => {
          setDiseases([]);
          setDiseasesError(friendlyErrorMessage(err, "Couldn't load diseases."));
        });
    }, 300);
    return () => clearTimeout(t);
  }, [search]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.predictSymptoms({
        fever,
        cough,
        fatigue,
        difficulty_breathing: difficultyBreathing,
        age,
        gender,
        blood_pressure: bloodPressure,
        cholesterol_level: cholesterol,
        symptoms: buildSymptomsPayload(advancedSymptoms),
      });
      setResults(res.predictions);
      setConfidenceLevel(res.confidence_level);
    } catch (err) {
      setError(friendlyErrorMessage(err, "Prediction failed. Please try again."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <PageLayout title="Symptom Analysis" subtitle={MEDICAL_DISCLAIMER}>
      <div className="space-y-8">
        <form onSubmit={onSubmit} className="page-card startup-form !my-0 max-w-none w-full space-y-6">
          {[
            ["Fever", fever, setFever],
            ["Cough", cough, setCough],
            ["Fatigue", fatigue, setFatigue],
            ["Difficulty Breathing", difficultyBreathing, setDifficultyBreathing],
          ].map(([label, val, setter]) => (
            <label key={label as string} className="flex justify-between items-center startup-form_label normal-case">
              <span>{label as string}</span>
              <input
                type="checkbox"
                checked={val as boolean}
                onChange={(e) => (setter as (v: boolean) => void)(e.target.checked)}
              />
            </label>
          ))}

          <AdvancedSymptomsPanel values={advancedSymptoms} onChange={setAdvancedSymptoms} />

          <label className="block">
            <span className="startup-form_label">Age</span>
            <input
              type="number"
              className="startup-form_input w-full"
              value={age}
              onChange={(e) => setAge(parseInt(e.target.value, 10) || 0)}
            />
          </label>

          <label className="block">
            <span className="startup-form_label">Gender</span>
            <select
              className="startup-form_input w-full"
              value={gender}
              onChange={(e) => setGender(e.target.value as "male" | "female")}
            >
              <option value="female">Female</option>
              <option value="male">Male</option>
            </select>
          </label>

          <label className="block">
            <span className="startup-form_label">Blood Pressure</span>
            <select
              className="startup-form_input w-full"
              value={bloodPressure}
              onChange={(e) => setBloodPressure(e.target.value as "normal" | "high" | "low")}
            >
              <option value="normal">Normal</option>
              <option value="high">High</option>
              <option value="low">Low</option>
            </select>
          </label>

          <label className="block">
            <span className="startup-form_label">Cholesterol Level</span>
            <select
              className="startup-form_input w-full"
              value={cholesterol}
              onChange={(e) => setCholesterol(e.target.value as "normal" | "high")}
            >
              <option value="normal">Normal</option>
              <option value="high">High</option>
            </select>
          </label>

          <button type="submit" disabled={loading} className="startup-form_btn disabled:opacity-50">
            {loading ? "Analyzing..." : "Get Predictions"}
          </button>
        </form>

        {error && <p className="startup-form_error">{error}</p>}

        {results && (
          <div className="page-card">
            <h2 className="page-card-title">Top predictions</h2>
            {confidenceLevel === "low" && (
              <p className="startup-card_desc text-amber-800 mb-4">
                Uncertain match — these are possibilities only. Please consult a qualified clinician.
              </p>
            )}
            {confidenceLevel === "medium" && (
              <p className="startup-card_desc mb-4">
                Moderate confidence — use as educational guidance, not a diagnosis.
              </p>
            )}
            <ul className="space-y-2">
              {results.map((r) => (
                <li key={r.disease} className="text-16-medium">
                  <Link href={`/disease/${r.slug}`} className="text-primary hover:underline">
                    {r.disease}
                  </Link>
                  : {(r.probability * 100).toFixed(1)}%
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="page-card">
          <h2 className="page-card-title">
            {search ? `Results for "${search}"` : "All diseases"}
          </h2>
          <div className="search-form mt-0 mb-6">
            <input
              type="search"
              placeholder="Search diseases..."
              className="search-input"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <ul className="card_grid">
            {diseasesError ? (
              <p className="no-result text-red-600">{diseasesError}</p>
            ) : diseases.length === 0 ? (
              <p className="no-result">No diseases found</p>
            ) : (
              diseases.map((d) => (
                <li key={d.slug} className="startup-card">
                  <h3 className="text-20-medium">{d.name}</h3>
                  {d.description && <p className="startup-card_desc">{d.description}</p>}
                  <Button className="startup-card_btn mt-4" asChild>
                    <Link href={`/disease/${d.slug}`}>Details</Link>
                  </Button>
                </li>
              ))
            )}
          </ul>
        </div>
      </div>
    </PageLayout>
  );
}
