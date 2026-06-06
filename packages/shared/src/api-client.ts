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
  SymptomPredictResponse,
  SymptomRequest,
} from "./types";

export type TokenProvider = () => Promise<string | null>;

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
      let body: ApiErrorBody | null = null;
      try {
        body = (await res.json()) as ApiErrorBody;
      } catch {
        /* ignore */
      }
      if (body?.error) {
        throw new ApiClientError(body.error.code, body.error.message, res.status);
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

  async scanPrescription(file: Blob | File) {
    const form = new FormData();
    form.append("file", file);
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
