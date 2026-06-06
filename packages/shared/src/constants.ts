export const MEDICAL_DISCLAIMER =
  "CureDesk provides informational content only and is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified healthcare provider.";

export const API_PATHS = {
  health: "/health",
  ready: "/ready",
  predictSymptoms: "/v1/symptoms/predict",
  symptomFeatures: "/v1/symptoms/features",
  diseases: "/v1/diseases",
  diseaseBySlug: (slug: string) => `/v1/diseases/${slug}`,
  scanPrescription: "/v1/prescriptions/scan",
  chat: "/v1/chat",
  profileHistory: "/v1/profile/history",
} as const;

export const OCR_LOADING_MESSAGE = "Analyzing prescription — this may take a moment.";
