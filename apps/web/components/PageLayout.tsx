import type { ReactNode } from "react";

type PageLayoutProps = {
  title: string;
  subtitle?: string;
  meta?: string;
  children: ReactNode;
  /** Constrain main content to a centered column */
  narrow?: boolean;
};

export default function PageLayout({ title, subtitle, meta, children, narrow }: PageLayoutProps) {
  return (
    <div className="min-h-screen bg-white-100 flex flex-col">
      <header className="blue_container !min-h-0 py-6 sm:py-8 relative shrink-0">
        <h1 className="heading !my-2">{title}</h1>
        {subtitle && <p className="sub-heading mt-1">{subtitle}</p>}
        {meta && <p className="text-14-normal mt-2">{meta}</p>}
      </header>

      <div
        className={`flex-1 w-full px-5 sm:px-8 lg:px-10 xl:px-12 py-8 sm:py-10 ${
          narrow ? "max-w-md mx-auto" : ""
        }`}
      >
        {children}
      </div>
    </div>
  );
}
