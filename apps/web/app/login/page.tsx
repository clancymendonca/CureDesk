"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import PageLayout from "@/components/PageLayout";
import { useAuth } from "@/lib/auth-context";
import { signInEmail, signUpEmail, signInGoogle } from "@/lib/firebase";

export default function LoginPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSignUp, setIsSignUp] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!authLoading && user) router.push("/profile");
  }, [authLoading, user, router]);

  async function googleSignIn() {
    setLoading(true);
    setError(null);
    try {
      await signInGoogle();
      router.push("/profile");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Google sign-in failed");
    } finally {
      setLoading(false);
    }
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (isSignUp) await signUpEmail(email, password);
      else await signInEmail(email, password);
      router.push("/profile");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <PageLayout
      title={isSignUp ? "Create Account" : "Log In"}
      subtitle="Sign in to save your activity and access your profile."
      narrow
    >
      <button
        type="button"
        onClick={googleSignIn}
        disabled={loading}
        className="login w-full mb-4 disabled:opacity-50"
      >
        Continue with Google
      </button>

      <form onSubmit={submit} className="page-card startup-form !my-0 space-y-6">
        <input
          type="email"
          placeholder="Email"
          className="startup-form_input w-full"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          className="startup-form_input w-full"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {error && <p className="startup-form_error">{error}</p>}
        <button type="submit" disabled={loading} className="startup-form_btn">
          {loading ? "..." : isSignUp ? "Sign Up" : "Sign In"}
        </button>
        <button
          type="button"
          onClick={() => setIsSignUp(!isSignUp)}
          className="text-16-medium text-primary w-full"
        >
          {isSignUp ? "Already have an account?" : "Need an account?"}
        </button>
      </form>

      <div className="mt-6 text-sm text-center space-x-4">
        <Link href="/terms" className="text-black-100 hover:text-primary">
          Terms
        </Link>
        <Link href="/privacy" className="text-black-100 hover:text-primary">
          Privacy
        </Link>
      </div>
    </PageLayout>
  );
}
