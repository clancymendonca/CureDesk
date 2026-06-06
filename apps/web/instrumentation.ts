import * as Sentry from "@sentry/nextjs";

export async function register() {
  if (process.env.NEXT_PUBLIC_SENTRY_DSN) {
    await import("./sentry.server.config");
  }
}

export const onRequestError = Sentry.captureRequestError;
