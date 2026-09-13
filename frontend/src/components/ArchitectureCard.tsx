import React from "react";
import { LucideIcon } from "lucide-react";

interface ArchitectureCardProps {
  title: string;
  badge: string;
  description: string;
  icon: LucideIcon;
  details: string[];
}

export function ArchitectureCard({
  title,
  badge,
  description,
  icon: Icon,
  details,
}: ArchitectureCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="w-10 h-10 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600">
            <Icon className="w-5 h-5" />
          </div>
          <span className="text-[11px] font-semibold tracking-wide uppercase px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
            {badge}
          </span>
        </div>
        <h3 className="text-base font-bold text-slate-900 mb-2">{title}</h3>
        <p className="text-sm text-slate-600 leading-relaxed mb-4">{description}</p>
      </div>

      <ul className="space-y-1.5 border-t border-slate-100 pt-4">
        {details.map((detail, idx) => (
          <li key={idx} className="flex items-center gap-2 text-xs text-slate-500">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span>{detail}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
