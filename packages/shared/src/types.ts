import type { components } from "./types.generated";

export type SymptomRequest = components["schemas"]["SymptomRequest"] & {
  symptoms?: Record<string, boolean>;
};
export type DiseasePrediction = components["schemas"]["DiseasePrediction"];
export type SymptomPredictResponse = components["schemas"]["SymptomPredictResponse"];
export type DiseaseSummary = components["schemas"]["DiseaseSummary"];
export type DiseaseListResponse = components["schemas"]["DiseaseListResponse"];
export type DrugMatch = components["schemas"]["DrugMatch"];
export type PrescriptionScanResponse = components["schemas"]["PrescriptionScanResponse"];
export type ChatMessage = components["schemas"]["ChatMessage"];
export type ChatRequest = components["schemas"]["ChatRequest"];
export type ChatResponse = components["schemas"]["ChatResponse"];
export type HistoryItem = components["schemas"]["HistoryItem"];
export type ProfileHistoryResponse = components["schemas"]["ProfileHistoryResponse"];

export interface SymptomFeaturesResponse {
  features: string[];
  model_version: string;
  feature_format: string;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
  };
}

export class ApiClientError extends Error {
  constructor(
    public code: string,
    message: string,
    public status: number
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}
