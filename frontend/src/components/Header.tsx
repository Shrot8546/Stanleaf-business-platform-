import React from "react";
import Link from "next/link";
import { Activity, Building2, ShieldCheck } from "lucide-react";

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200/80 bg-white/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo & Name */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-lg bg-emerald-600 flex items-center justify-center text-white shadow-sm shadow-emerald-500/20 group-hover:bg-emerald-700 transition-colors">
            <Activity className="w-5 h-5" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-lg tracking-tight text-slate-900 leading-none">
              Stanleaf
            </span>
            <span className="text-[10px] uppercase font-semibold tracking-wider text-emerald-600 mt-0.5">
              Health Intelligence
            </span>
          </div>
        </Link>

        {/* Navigation / Links */}
        <nav className="flex items-center gap-4 sm:gap-6 text-sm font-medium text-slate-600">
          <Link
            href="/onboarding"
            className="flex items-center gap-1.5 text-emerald-700 hover:text-emerald-800 font-semibold px-3 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100/80 transition-colors border border-emerald-200/60 text-xs sm:text-sm"
          >
            <Building2 className="w-4 h-4 text-emerald-600" /> Register Business
          </Link>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:inline-block hover:text-emerald-600 transition-colors text-xs sm:text-sm"
          >
            API Docs
          </a>
          <span className="hidden sm:flex px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200 items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" /> v0.2.0 Core
          </span>
        </nav>
      </div>
    </header>
  );
}
