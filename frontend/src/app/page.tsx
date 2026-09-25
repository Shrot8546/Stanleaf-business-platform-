import React from "react";
import Link from "next/link";
import {
  Calculator,
  LineChart,
  AlertTriangle,
  Lightbulb,
  Database,
  Cpu,
  Layers,
  Sparkles,
  Building2,
} from "lucide-react";
import { HealthStatusBadge } from "@/components/HealthStatusBadge";
import { ArchitectureCard } from "@/components/ArchitectureCard";

export default function HomePage() {
  const pillars = [
    {
      title: "Explainable Health Scoring",
      badge: "Data Engine / Scoring",
      description:
        "Deterministic, multi-factor scoring model combining financial stability, operational efficiency, and market indicators with full mathematical transparency.",
      icon: Calculator,
      details: [
        "Weighted multi-dimensional indices",
        "Explainable factor contribution breakdown",
        "Strictly verifiable calculations",
      ],
    },
    {
      title: "Peer Benchmarking",
      badge: "Data Engine / Analytics",
      description:
        "Statistical cohort analysis grouping businesses by industry codes, operational stage, and scale to compute distribution percentiles.",
      icon: LineChart,
      details: [
        "Industry NAICS/SIC cohort clustering",
        "25th, 50th, 75th percentile distributions",
        "Relative market positioning metrics",
      ],
    },
    {
      title: "Risk & Trend Modeling",
      badge: "ML Pipeline Layer",
      description:
        "Time-series and gradient-boosted decision trees trained on historical business indicators to flag liquidity crunches and runway risks.",
      icon: AlertTriangle,
      details: [
        "Feature store for financial indicators",
        "Model training and cross-validation suite",
        "SHAP-based feature importance explainability",
      ],
    },
    {
      title: "Actionable Recommendations",
      badge: "Local AI / Ollama",
      description:
        "Contextual natural language synthesis driven by local, privacy-first LLMs converting quantitative score gaps into concrete management actions.",
      icon: Lightbulb,
      details: [
        "Self-hosted local inference with Ollama",
        "Privacy-preserving owner data processing",
        "Structured recommendation schemas",
      ],
    },
  ];

  return (
    <div className="flex flex-col items-center">
      {/* Hero Section */}
      <section className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 text-center">
        {/* Capstone Badge */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/80 mb-8 shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
          <span>CSE Capstone — Data Science & Big Data Analytics</span>
        </div>

        {/* Primary Title */}
        <h1 className="text-5xl sm:text-6xl md:text-7xl font-extrabold text-slate-900 tracking-tight leading-none mb-6">
          Stanleaf
        </h1>

        {/* Subtitle / Tagline */}
        <p className="text-2xl sm:text-3xl font-medium text-slate-700 tracking-tight mb-4">
          Business Intelligence, Simplified.
        </p>

        {/* Vision Narrative */}
        <p className="max-w-2xl mx-auto text-base sm:text-lg text-slate-500 leading-relaxed mb-8">
          A startup-grade intelligence platform engineered to analyze business performance,
          calculate an explainable Business Health Score, benchmark against comparable peers,
          and surface actionable operational strategies.
        </p>

        {/* Call to Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-10">
          <Link
            href="/onboarding"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm transition-colors shadow-sm"
          >
            <Building2 className="w-4 h-4" />
            <span>Register a Business</span>
          </Link>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-50 font-semibold text-sm transition-colors"
          >
            <span>Explore API Docs</span>
          </a>
        </div>

        {/* Live Backend Health Status Badge */}
        <HealthStatusBadge />
      </section>

      {/* Architectural Separation Highlights */}
      <section className="w-full bg-white border-y border-slate-200/80 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Foundational Software Architecture
            </h2>
            <p className="text-sm sm:text-base text-slate-500 mt-2">
              Clean separation of concerns with a dedicated Data Science & Analytics layer,
              FastAPI backend, PostgreSQL relational model, and Next.js frontend.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {pillars.map((pillar, idx) => (
              <ArchitectureCard key={idx} {...pillar} />
            ))}
          </div>
        </div>
      </section>

      {/* Layer Specs Grid */}
      <section className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-6">
            <div className="flex items-center gap-3 mb-3 text-slate-900 font-semibold">
              <Layers className="w-5 h-5 text-emerald-600" />
              <span>Modular Data Engine</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Separated packages for <code className="text-emerald-700 font-mono">ingestion</code>,{" "}
              <code className="text-emerald-700 font-mono">cleaning</code>,{" "}
              <code className="text-emerald-700 font-mono">features</code>,{" "}
              <code className="text-emerald-700 font-mono">analytics</code>, and{" "}
              <code className="text-emerald-700 font-mono">scoring</code>.
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-6">
            <div className="flex items-center gap-3 mb-3 text-slate-900 font-semibold">
              <Cpu className="w-5 h-5 text-emerald-600" />
              <span>FastAPI Backend</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              High-performance asynchronous Python API with strict Pydantic schemas,
              configured CORS policies for Next.js, and versioned router architecture.
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-6">
            <div className="flex items-center gap-3 mb-3 text-slate-900 font-semibold">
              <Database className="w-5 h-5 text-emerald-600" />
              <span>Structured Relational Core</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              PostgreSQL schema blueprints modeling organizations, period-based financial metrics,
              operational indicators, benchmark distributions, and score records.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
