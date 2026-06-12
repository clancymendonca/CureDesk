"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { friendlyErrorMessage, HistoryItem } from "@curedesk/shared";
import PageLayout from "@/components/PageLayout";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";

export default function ProfilePage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [historyLoading, setHistoryLoading] = useState(true);

  useEffect(() => {
    if (loading) return;
    if (!user) {
      router.push("/login");
      return;
    }
    setHistoryLoading(true);
    setHistoryError(null);
    api
      .profileHistory()
      .then((r) => setHistory(r.items))
      .catch((err) => setHistoryError(friendlyErrorMessage(err)))
      .finally(() => setHistoryLoading(false));
  }, [user, loading, router]);

  if (loading || !user) return null;

  return (
    <PageLayout
      title="Profile"
      subtitle={user.displayName ?? user.email ?? undefined}
    >
      <div className="grid lg:grid-cols-[minmax(240px,280px)_minmax(0,1fr)] gap-6 lg:gap-8 xl:gap-10">
        <aside className="page-card h-fit">
          <h2 className="page-card-title !text-lg">Account</h2>
          <p className="text-16-medium">{user.email}</p>
          {user.displayName && (
            <p className="text-16-medium text-black-100 mt-2">{user.displayName}</p>
          )}
        </aside>

        <div className="page-card">
          <h2 className="page-card-title">Recent activity</h2>
          {historyLoading ? (
            <p className="no-result">Loading…</p>
          ) : historyError ? (
            <p className="no-result text-red-600">{historyError}</p>
          ) : history.length === 0 ? (
            <p className="no-result">No history yet</p>
          ) : (
            <ul className="space-y-3">
              {history.map((h) => (
                <li
                  key={h.id}
                  className="text-sm text-black-100 border-b-[2px] border-black/10 pb-3 last:border-0 last:pb-0"
                >
                  <span className="block text-xs uppercase tracking-wide text-black/50">
                    {h.type === "symptom" ? "Symptom check" : "Prescription scan"} ·{" "}
                    {formatDate(h.created_at)}
                  </span>
                  {h.summary}
                </li>
              ))}
            </ul>
          )}

          <div className="mt-8 pt-6 border-t-[3px] border-black text-sm space-x-4">
            <Link href="/terms" className="text-primary hover:underline">
              Terms
            </Link>
            <Link href="/privacy" className="text-primary hover:underline">
              Privacy
            </Link>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}
