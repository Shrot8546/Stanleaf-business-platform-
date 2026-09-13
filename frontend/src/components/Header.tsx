import React from "react";
import Link from "next/link";
import { Activity, Layers, ShieldCheck } from "lucide-react";

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
        <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-600">
          <span className="flex items-center gap-1.5 text-slate-900 font-semibold">
            <Layers className="w-4 h-4 text-emerald-600" /> Architecture Foundation
          </span>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-emerald-600 transition-colors"
          >
            API Docs
          </a>
          <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/60 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5" /> v0.1.0 Core
          </span>
        </nav>
      </div>
    </header>
  );
}
