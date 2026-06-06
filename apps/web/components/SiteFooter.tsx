import Link from "next/link";

export default function SiteFooter() {
  return (
    <footer className="bg-cyan-500 px-6 py-8 border-t border-teal-900/10">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <p className="text-sm font-medium text-teal-950/80">
          © {new Date().getFullYear()} CureDesk
        </p>
        <nav aria-label="Legal" className="flex items-center gap-6 text-sm">
          <Link href="/terms" className="text-teal-950 font-medium hover:text-primary">
            Terms of Service
          </Link>
          <Link href="/privacy" className="text-teal-950 font-medium hover:text-primary">
            Privacy Policy
          </Link>
        </nav>
      </div>
    </footer>
  );
}
