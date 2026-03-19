import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Script from "next/script";
import Link from "next/link";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Drug Discovery Co Pilot",
  description: "Autonomous agents for early-stage target discovery and lead generation.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.variable} font-sans antialiased bg-[#030712] text-slate-300 min-h-screen selection:bg-blue-500/30 selection:text-blue-200 relative`}
        suppressHydrationWarning
      >
        {/* Global ambient background glow */}
        <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
          <div className="absolute top-[-25%] left-[-10%] w-[50%] h-[50%] bg-blue-900/20 blur-[120px] rounded-full mix-blend-screen"></div>
          <div className="absolute bottom-[-30%] right-[-10%] w-[50%] h-[60%] bg-emerald-900/10 blur-[150px] rounded-full mix-blend-screen"></div>
        </div>

        <div className="flex flex-col min-h-screen relative z-10">
          <header className="sticky top-0 z-50 bg-[#030712]/70 backdrop-blur-xl border-b border-white/5 supports-[backdrop-filter]:bg-[#030712]/50">
            <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
              <div className="flex items-center gap-3 cursor-pointer group">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-xl shadow-[0_0_20px_rgba(59,130,246,0.3)] group-hover:shadow-[0_0_25px_rgba(59,130,246,0.6)] group-hover:scale-105 transition-all duration-300">
                  🧬
                </div>
                <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-1.5">
                  AI Drug Discovery <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400 font-semibold">Co Pilot</span>
                </h1>
              </div>
              <nav className="flex gap-8 text-sm font-semibold tracking-wide text-slate-400">
                <Link href="/" className="hover:text-white transition-colors duration-300">Dashboard</Link>
                <Link href="/architecture" className="hover:text-white transition-colors duration-300">Architecture</Link>
              </nav>
            </div>
          </header>
          
          <main className="flex-1 max-w-7xl mx-auto px-6 py-12 w-full">
            {children}
          </main>
          
          <footer className="border-t border-white/5 py-8 mt-auto">
            <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4 text-xs font-semibold tracking-widest uppercase text-slate-600">
              <span>© 2026 Proprietary of Shivam Dixit</span>
              <span className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/5">
                <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)] animate-pulse"></span>
                <span className="text-slate-400">Core Systems Operational</span>
              </span>
            </div>
          </footer>
        </div>
        
        {/* Load 3Dmol globally */}
        <Script src="https://3Dmol.org/build/3Dmol-min.js" strategy="beforeInteractive" />
      </body>
    </html>
  );
}
