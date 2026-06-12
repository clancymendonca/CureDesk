"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { signOut } from "@/lib/firebase";

export default function Navbar() {
  const { user, loading } = useAuth();
  const router = useRouter();

  const handleSignOut = async () => {
    try {
      await signOut();
    } finally {
      router.push("/");
    }
  };

  return (
    <header className="px-5 py-3 bg-cyan-500 shadow-sm font-work-sans">
      <nav className="flex justify-between items-center">
        <Link href="/" className="mx-10 flex items-center gap-2.5">
          <Image
            src="/logo-icon.png"
            alt=""
            width={36}
            height={36}
            priority
            className="h-9 w-9"
            aria-hidden
          />
          <Image
            src="/logo-wordmark.png"
            alt="CureDesk"
            width={160}
            height={40}
            priority
            className="h-7 w-auto brightness-0"
          />
        </Link>
        <div className="flex items-center gap-5 text-black">
          {loading ? null : user ? (
            <>
              <button
                type="button"
                onClick={handleSignOut}
                className="relative flex justify-center px-6 py-3 before:absolute before:inset-0 before:rounded-lg before:transition before:bg-gray-100 text-indigo-600 hover:before:scale-105"
              >
                <span className="relative">LogOut</span>
              </button>
              <Link href="/profile">
                <span>{user.displayName ?? user.email}</span>
              </Link>
            </>
          ) : (
            <Link
              href="/login"
              className="relative flex justify-center px-6 py-3 before:absolute before:inset-0 before:rounded-lg before:transition before:bg-gray-100 text-indigo-600 hover:before:scale-105"
            >
              <span className="relative">LogIn</span>
            </Link>
          )}
        </div>
      </nav>
    </header>
  );
}
