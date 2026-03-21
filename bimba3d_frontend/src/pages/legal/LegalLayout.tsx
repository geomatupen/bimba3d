import { Link, useLocation } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import type { ReactNode } from "react";

type LegalLayoutProps = {
  title: string;
  updatedAt: string;
  children: ReactNode;
};

const navItems = [
  { to: "/legal/terms", label: "Terms" },
  { to: "/legal/privacy", label: "Privacy" },
  { to: "/legal/dpa", label: "DPA" },
  { to: "/legal/security", label: "Security" },
  { to: "/legal/compliance", label: "Compliance" },
  { to: "/legal/third-party-notices", label: "Third-Party Notices" },
];

export default function LegalLayout({ title, updatedAt, children }: LegalLayoutProps) {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50">
      <header className="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 shadow-xl">
        <div className="max-w-6xl mx-auto px-6 lg:px-8 py-6">
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <Link
                to="/"
                className="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20 text-white text-sm font-medium transition-all duration-200"
              >
                <ArrowLeft className="w-4 h-4" />
                Back
              </Link>
              <span className="text-xs px-2 py-1 rounded-md bg-white/15 border border-white/20 text-blue-50">
                Legal & Trust
              </span>
            </div>
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-white mb-1">{title}</h1>
              <p className="text-blue-100 text-sm">Last updated: {updatedAt}</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 lg:px-8 py-6 space-y-6">
        <nav className="flex flex-wrap gap-2 rounded-xl border border-slate-200 bg-white p-2 shadow-sm">
          {navItems.map((item) => {
            const active = location.pathname === item.to;
            return (
              <Link
                key={item.to}
                to={item.to}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  active
                    ? "bg-blue-600 text-white"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <section className="rounded-2xl border border-slate-200 bg-white shadow-sm p-6 lg:p-8 text-slate-700 leading-7 text-sm lg:text-base space-y-5">
          {children}
        </section>
      </main>
    </div>
  );
}
