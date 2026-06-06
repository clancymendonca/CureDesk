import Link from "next/link";
import type { ReactNode } from "react";
import PageLayout from "@/components/PageLayout";

export type LegalSection = {
  id: string;
  title: string;
  content: ReactNode;
};

type LegalPageLayoutProps = {
  title: string;
  subtitle: string;
  lastUpdated: string;
  sections: LegalSection[];
  relatedLink: { href: string; label: string };
};

function TableOfContents({ sections }: { sections: LegalSection[] }) {
  return (
    <ol className="space-y-2.5">
      {sections.map((section, index) => (
        <li key={section.id}>
          <a
            href={`#${section.id}`}
            className="text-[15px] text-black-100 leading-snug hover:text-primary transition-colors"
          >
            <span className="text-black-300 mr-1.5">{index + 1}.</span>
            {section.title}
          </a>
        </li>
      ))}
    </ol>
  );
}

export default function LegalPageLayout({
  title,
  subtitle,
  lastUpdated,
  sections,
  relatedLink,
}: LegalPageLayoutProps) {
  return (
    <PageLayout title={title} subtitle={subtitle} meta={`Last updated: ${lastUpdated}`}>
      <div className="grid lg:grid-cols-[minmax(240px,280px)_minmax(0,1fr)] gap-6 lg:gap-8 xl:gap-10 min-h-0">
        <aside className="hidden lg:block min-w-0">
          <nav aria-label="Table of contents" className="page-card sticky top-8 h-fit !py-6">
            <p className="text-xs font-semibold uppercase tracking-wider text-black-300 mb-4">
              Contents
            </p>
            <TableOfContents sections={sections} />
          </nav>
        </aside>

        <div className="min-w-0 flex flex-col">
          <nav
            aria-label="Table of contents"
            className="page-card lg:hidden mb-6 !py-4"
          >
            <p className="text-xs font-semibold uppercase tracking-wider text-black-300 mb-3">
              On this page
            </p>
            <TableOfContents sections={sections} />
          </nav>

          <article className="page-card flex-1 lg:px-12">
            <div className="space-y-12">
              {sections.map((section) => (
                <section key={section.id} id={section.id} className="scroll-mt-24">
                  <h2 className="page-card-title">{section.title}</h2>
                  <div className="legal-body">{section.content}</div>
                </section>
              ))}
            </div>
          </article>

          <footer className="mt-8 pt-6 border-t-[3px] border-black flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 text-sm">
            <p className="text-black-300">Questions? Reach out through the CureDesk website.</p>
            <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
              <Link href={relatedLink.href} className="font-medium text-primary hover:underline">
                {relatedLink.label}
              </Link>
              <Link href="/" className="text-black-100 hover:text-primary transition-colors">
                Home
              </Link>
            </div>
          </footer>
        </div>
      </div>
    </PageLayout>
  );
}
