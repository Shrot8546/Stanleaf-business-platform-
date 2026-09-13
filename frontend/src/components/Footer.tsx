import React from "react";

export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white py-8 text-center text-sm text-slate-500">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <p>© {new Date().getFullYear()} Stanleaf. Business Health Intelligence Platform.</p>
        <p className="text-xs text-slate-400">
          Data Science & Big Data Analytics Capstone Architecture
        </p>
      </div>
    </footer>
  );
}
