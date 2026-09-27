import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/layout/Navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "StepSolve — Numerical Methods Calculator",
  description:
    "Interactive step-by-step numerical methods calculator covering all 5 modules: Root Finding, Systems, Interpolation, Calculus, ODEs, and BVPs.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.className} min-h-screen bg-slate-950 text-slate-100 antialiased selection:bg-indigo-500/30 selection:text-indigo-200`}
      >
        <div className="relative flex min-h-screen flex-col">
          <Navbar />
          <main className="flex-1">{children}</main>
          <footer className="border-t border-white/5 py-8 text-center text-xs text-slate-500">
            <div className="mx-auto max-w-7xl px-4">
              <p className="font-medium text-slate-400">
                StepSolve — Numerical Methods & Applications
              </p>
              <p className="mt-1">
                VII Semester CSE · Sahyadri College of Engineering & Management
              </p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
