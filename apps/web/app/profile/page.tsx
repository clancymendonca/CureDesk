"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import PageLayout from "@/components/PageLayout";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";

export default function ProfilePage() {
  const user = useAuth();
  const router = useRouter();
  const [history, setHistory] = useState<{ summary: string; created_at: string }[]>([]);

  useEffect(() => {
    if (user === null) return;
    if (!user) {
      router.push("/login");
      return;
    }
    api.profileHistory().then((r) => setHistory(r.items)).catch(() => setHistory([]));
  }, [user, router]);

  if (!user) return null;

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
          {history.length === 0 ? (
            <p className="no-result">No history yet</p>
          ) : (
            <ul className="space-y-3">
              {history.map((h, i) => (
                <li
                  key={i}
                  className="text-sm text-black-100 border-b-[2px] border-black/10 pb-3 last:border-0 last:pb-0"
                >
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
