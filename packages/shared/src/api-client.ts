import { API_PATHS } from "./constants";
import {
  ApiClientError,
  ApiErrorBody,
  ChatRequest,
  ChatResponse,
  DiseaseListResponse,
  DiseaseSummary,
  PrescriptionScanResponse,
  ProfileHistoryResponse,
  SymptomFeaturesResponse,
  SymptomPredictResponse,
  SymptomRequest,
} from "./types";

export type TokenProvider = () => Promise<string | null>;

/** React Native FormData file descriptor ({ uri, name, type }). */
export interface NativeFilePart {
  uri: string;
  name: string;
  type: string;
}

export type UploadFile = Blob | File | NativeFilePart;

export class CureDeskApiClient {
  constructor(
    private baseUrl: string,
    private getToken?: TokenProvider
  ) {}

  private async headers(contentType?: string): Promise<HeadersInit> {
    const h: Record<string, string> = {};
    if (contentType) h["Content-Type"] = contentType;
    const token = this.getToken ? await this.getToken() : null;
    if (token) h["Authorization"] = `Bearer ${token}`;
    return h;
  }

  private async handle<T>(res: Response): Promise<T> {
    if (!res.ok) {
      let body: unknown = null;
      try {
        body = await res.json();
      } catch {
        /* ignore */
      }
      // FastAPI wraps custom error payloads in "detail"; unwrap both shapes.
      const raw = body as
        | { error?: unknown; detail?: { error?: unknown } | string }
        | null;
      const err =
        raw?.error ??
        (typeof raw?.detail === "object" ? raw?.detail?.error : raw?.detail);
      if (err && typeof err === "object") {
        const e = err as ApiErrorBody["error"];
        throw new ApiClientError(e.code ?? "UNKNOWN", e.message ?? res.statusText, res.status);
      }
      if (typeof err === "string") {
        // e.g. slowapi rate-limit responses use a plain string error body
        const code = res.status === 429 ? "RATE_LIMITED" : "UNKNOWN";
        throw new ApiClientError(code, err, res.status);
      }
      throw new ApiClientError("UNKNOWN", res.statusText, res.status);
    }
    return res.json() as Promise<T>;
  }

  async health() {
    const res = await fetch(`${this.baseUrl}${API_PATHS.health}`);
    return this.handle<{ status: string }>(res);
  }

  async ready() {
    const res = await fetch(`${this.baseUrl}${API_PATHS.ready}`);
    return this.handle<{ status: string; db: boolean; ml: boolean }>(res);
  }

  async getSymptomFeatures() {
    const res = await fetch(`${this.baseUrl}${API_PATHS.symptomFeatures}`);
    return this.handle<SymptomFeaturesResponse>(res);
  }

  async predictSymptoms(data: SymptomRequest) {
    const res = await fetch(`${this.baseUrl}${API_PATHS.predictSymptoms}`, {
      method: "POST",
      headers: await this.headers("application/json"),
      body: JSON.stringify(data),
    });
    return this.handle<SymptomPredictResponse>(res);
  }

  async listDiseases(q?: string) {
    const url = new URL(`${this.baseUrl}${API_PATHS.diseases}`);
    if (q) url.searchParams.set("q", q);
    const res = await fetch(url.toString());
    return this.handle<DiseaseListResponse>(res);
  }

  async getDisease(slug: string) {
    const res = await fetch(`${this.baseUrl}${API_PATHS.diseaseBySlug(slug)}`);
    return this.handle<DiseaseSummary>(res);
  }

  async scanPrescription(file: UploadFile) {
    const form = new FormData();
    // React Native accepts { uri, name, type } descriptors; browsers take Blob/File.
    form.append("file", file as Blob);
    const res = await fetch(`${this.baseUrl}${API_PATHS.scanPrescription}`, {
      method: "POST",
      headers: await this.headers(),
      body: form,
    });
    return this.handle<PrescriptionScanResponse>(res);
  }

  async chat(data: ChatRequest) {
    const res = await fetch(`${this.baseUrl}${API_PATHS.chat}`, {
      method: "POST",
      headers: await this.headers("application/json"),
      body: JSON.stringify(data),
    });
    return this.handle<ChatResponse>(res);
  }

  async profileHistory() {
    const res = await fetch(`${this.baseUrl}${API_PATHS.profileHistory}`, {
      headers: await this.headers(),
    });
    return this.handle<ProfileHistoryResponse>(res);
  }
}

export function createApiClient(baseUrl: string, getToken?: TokenProvider) {
  return new CureDeskApiClient(baseUrl, getToken);
}
