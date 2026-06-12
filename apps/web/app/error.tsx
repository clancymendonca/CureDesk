"use client";

import PageLayout from "@/components/PageLayout";

export default function GlobalError({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <PageLayout title="Something went wrong" narrow>
      <div className="page-card text-center space-y-4">
        <p className="text-16-medium">
          An unexpected error occurred. Please try again.
        </p>
        <button
          type="button"
          onClick={reset}
          className="startup-form_btn !w-auto px-6"
        >
          Try again
        </button>
      </div>
    </PageLayout>
  );
}
