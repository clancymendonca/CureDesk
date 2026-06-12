import Link from "next/link";
import PageLayout from "@/components/PageLayout";

export default function NotFound() {
  return (
    <PageLayout title="Page not found" narrow>
      <div className="page-card text-center space-y-4">
        <p className="text-16-medium">
          We couldn&apos;t find the page you were looking for.
        </p>
        <Link href="/" className="text-primary hover:underline">
          Back to home
        </Link>
      </div>
    </PageLayout>
  );
}
