import { ApiClientError } from "./types";

const CODE_MESSAGES: Record<string, string> = {
  ML_NOT_READY:
    "The prediction model is still starting up. Please try again in a minute.",
  CHAT_UNAVAILABLE:
    "The chat assistant is temporarily unavailable. Please try again later.",
  OCR_TIMEOUT:
    "Reading the image took too long. Please try a clearer, well-lit photo.",
  OCR_FAILED: "We couldn't read that image. Please try a clearer, well-lit photo.",
  INVALID_FILE: "Only JPEG and PNG images are supported.",
  FILE_TOO_LARGE: "That image is too large. Please upload one under 5MB.",
  UNAUTHENTICATED: "Please sign in to continue.",
  UNAUTHORIZED: "Please sign in to continue.",
  VALIDATION_ERROR: "Some of the information you entered isn't valid. Please review and try again.",
};

/** Map any thrown error to a user-friendly message. */
export function friendlyErrorMessage(
  err: unknown,
  fallback = "Something went wrong. Please try again."
): string {
  if (err instanceof ApiClientError) {
    if (err.status === 429) {
      return "Too many requests — please wait a moment and try again.";
    }
    const mapped = err.code ? CODE_MESSAGES[err.code] : undefined;
    if (mapped) return mapped;
    if (err.status === 404) return "We couldn't find what you were looking for.";
    if (err.status >= 500) return "The server had a problem. Please try again shortly.";
    return err.message || fallback;
  }
  if (err instanceof TypeError) {
    return "Can't reach the CureDesk server. Check your connection and try again.";
  }
  return fallback;
}

export function isNotFoundError(err: unknown): boolean {
  return err instanceof ApiClientError && err.status === 404;
}

export function isRetryableError(err: unknown): boolean {
  if (err instanceof ApiClientError) {
    return err.status === 429 || err.status === 503 || err.status === 504;
  }
  return err instanceof TypeError;
}
