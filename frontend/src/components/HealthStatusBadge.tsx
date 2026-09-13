"use client";

import React, { useEffect, useState, useCallback } from "react";
import { CheckCircle2, AlertCircle, RefreshCw, Server } from "lucide-react";
import { fetchHealthStatus, HealthResponse } from "@/lib/api";

export function HealthStatusBadge() {
  const [data, setData] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchHealthStatus();
      setData(res);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Unable to connect to backend";
      setError(message);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    // Poll health check every 15 seconds
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  return (
    <div className="w-full max-w-xl mx-auto rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:shadow-md">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-3">
        <div className="flex items-center gap-2">
          <Server className="w-4 h-4 text-slate-500" />
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Backend Health Status
          </span>
        </div>
        <button
          onClick={checkHealth}
          disabled={loading}
          aria-label="Refresh backend status"
          className="flex items-center gap-1.5 text-xs font-medium text-slate-600 hover:text-emerald-600 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh</span>
        </button>
      </div>

      {loading && !data && (
        <div className="flex items-center gap-3 text-slate-600 py-1">
          <div className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping" />
          <span className="text-sm font-medium">Checking backend connection...</span>
        </div>
      )}

      {data && (
        <div className="space-y-2.5">
          <div className="flex items-center gap-2 text-emerald-600">
            <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
            <span className="text-sm font-semibold tracking-tight text-emerald-950">
              FastAPI Core Online & Healthy
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
            <div className="bg-slate-50 rounded-lg p-2 border border-slate-100">
              <span className="text-[10px] uppercase font-bold text-slate-400 block">Service</span>
              <span className="text-xs font-semibold text-slate-700 truncate block">
                {data.service}
              </span>
            </div>
            <div className="bg-slate-50 rounded-lg p-2 border border-slate-100">
              <span className="text-[10px] uppercase font-bold text-slate-400 block">Status</span>
              <span className="text-xs font-semibold text-emerald-600 capitalize block">
                {data.status}
              </span>
            </div>
            <div className="bg-slate-50 rounded-lg p-2 border border-slate-100">
              <span className="text-[10px] uppercase font-bold text-slate-400 block">Version</span>
              <span className="text-xs font-semibold text-slate-700 block">v{data.version}</span>
            </div>
            <div className="bg-slate-50 rounded-lg p-2 border border-slate-100">
              <span className="text-[10px] uppercase font-bold text-slate-400 block">Environment</span>
              <span className="text-xs font-semibold text-slate-700 capitalize block">
                {data.environment}
              </span>
            </div>
          </div>
        </div>
      )}

      {error && !loading && (
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-amber-600">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span className="text-sm font-semibold text-slate-900">
              Backend Offline or Unreachable
            </span>
          </div>
          <p className="text-xs text-slate-500 leading-relaxed">
            Ensure the FastAPI server is running locally on port 8000:
          </p>
          <code className="block bg-slate-900 text-emerald-400 text-xs font-mono p-2.5 rounded-lg overflow-x-auto">
            uvicorn app.main:app --reload --port 8000
          </code>
        </div>
      )}
    </div>
  );
}
