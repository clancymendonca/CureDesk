"use client";

import { Suspense } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "@/lib/auth-context";
import Navbar from "@/components/Navbar";
import Chatbot from "@/components/Chatbot";
import { Skeleton } from "@/components/ui/skeleton";

const queryClient = new QueryClient();

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <main className="font-work-sans">
          <Navbar />
          {children}
          <Suspense fallback={<Skeleton className="chatbot_skeleton" />}>
            <Chatbot />
          </Suspense>
        </main>
      </AuthProvider>
    </QueryClientProvider>
  );
}
