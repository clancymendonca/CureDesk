import { createApiClient } from "@curedesk/shared";
import { getIdToken } from "./firebase";

const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const api = createApiClient(baseUrl, getIdToken);
