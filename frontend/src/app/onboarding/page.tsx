"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Building2,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
  ArrowLeft,
  Loader2,
  Sparkles,
} from "lucide-react";
import { createBusiness, Business } from "@/lib/api";

const REVENUE_RANGES = [
  "Pre-revenue / Seed",
  "Under ₹10 Lakhs ($12K)",
  "₹10L - ₹25L ($12K - $30K)",
  "₹25L - ₹50L ($30K - $60K)",
  "₹50L - ₹1 Crore ($60K - $120K)",
  "₹1Cr - ₹5 Crore ($120K - $600K)",
  "₹5Cr - ₹25 Crore ($600K - $3M)",
  "₹25 Crore+ ($3M+)",
];

const COMMON_INDUSTRIES = [
  "Software & SaaS",
  "Artificial Intelligence / ML",
  "E-Commerce & D2C",
  "FinTech & Financial Services",
  "Healthcare & MedTech",
  "Manufacturing & Industrial",
  "Logistics & Supply Chain",
  "Retail & Consumer Goods",
  "CleanTech & Energy",
  "Other",
];

export default function OnboardingPage() {
  const [formData, setFormData] = useState({
    name: "",
    industry: "",
    customIndustry: "",
    location: "",
    website: "",
    business_age_years: "",
    revenue_range: "",
    employee_count: "",
    customer_count: "",
    marketing_spend_monthly: "",
  });

  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [clientErrors, setClientErrors] = useState<Record<string, string>>({});
  const [createdBusiness, setCreatedBusiness] = useState<Business | null>(null);
  const [copiedId, setCopiedId] = useState(false);

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.name.trim()) {
      errors.name = "Business name is required.";
    }

    const effectiveIndustry =
      formData.industry === "Other"
        ? formData.customIndustry.trim()
        : formData.industry.trim();
    if (!effectiveIndustry) {
      errors.industry = "Industry sector is required.";
    }

    if (!formData.location.trim()) {
      errors.location = "Operating location is required.";
    }

    if (formData.website.trim()) {
      const urlPattern =
        /^(https?:\/\/)?([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(:\d{1,5})?(\/[^\s]*)?$/i;
      if (!urlPattern.test(formData.website.trim())) {
        errors.website = "Enter a valid website URL (e.g., https://example.com or example.com).";
      }
    }

    if (formData.business_age_years !== "") {
      const val = Number(formData.business_age_years);
      if (isNaN(val) || val < 0) {
        errors.business_age_years = "Business age must be a positive number.";
      }
    }

    if (formData.employee_count !== "") {
      const val = Number(formData.employee_count);
      if (isNaN(val) || val < 0) {
        errors.employee_count = "Employee count cannot be negative.";
      }
    }

    if (formData.customer_count !== "") {
      const val = Number(formData.customer_count);
      if (isNaN(val) || val < 0) {
        errors.customer_count = "Customer count cannot be negative.";
      }
    }

    if (formData.marketing_spend_monthly !== "") {
      const val = Number(formData.marketing_spend_monthly);
      if (isNaN(val) || val < 0) {
        errors.marketing_spend_monthly = "Marketing spend cannot be negative.";
      }
    }

    setClientErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (clientErrors[name]) {
      setClientErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const effectiveIndustry =
        formData.industry === "Other"
          ? formData.customIndustry.trim()
          : formData.industry.trim();

      const payload = {
        name: formData.name.trim(),
        industry: effectiveIndustry,
        location: formData.location.trim(),
        website: formData.website.trim() || undefined,
        business_age_years:
          formData.business_age_years !== ""
            ? parseInt(formData.business_age_years, 10)
            : undefined,
        revenue_range: formData.revenue_range.trim() || undefined,
        employee_count:
          formData.employee_count !== ""
            ? parseInt(formData.employee_count, 10)
            : undefined,
        customer_count:
          formData.customer_count !== ""
            ? parseInt(formData.customer_count, 10)
            : undefined,
        marketing_spend_monthly:
          formData.marketing_spend_monthly !== ""
            ? parseFloat(formData.marketing_spend_monthly)
            : undefined,
      };

      const result = await createBusiness(payload);
      setCreatedBusiness(result);
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "An unexpected error occurred while registering the business.";
      setErrorMessage(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyId = () => {
    if (createdBusiness?.id) {
      navigator.clipboard.writeText(createdBusiness.id);
      setCopiedId(true);
      setTimeout(() => setCopiedId(false), 2500);
    }
  };

  const handleReset = () => {
    setCreatedBusiness(null);
    setFormData({
      name: "",
      industry: "",
      customIndustry: "",
      location: "",
      website: "",
      business_age_years: "",
      revenue_range: "",
      employee_count: "",
      customer_count: "",
      marketing_spend_monthly: "",
    });
    setClientErrors({});
    setErrorMessage(null);
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Back button */}
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 transition-colors mb-8"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Home</span>
      </Link>

      {/* Header */}
      <div className="mb-10 text-center sm:text-left">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/80 mb-3">
          <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
          <span>Step 2 — Business Registration & Persistence</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          Business Onboarding
        </h1>
        <p className="text-slate-500 text-sm sm:text-base mt-2">
          Register your business entity into Stanleaf to initialize its relational record in PostgreSQL.
        </p>
      </div>

      {/* Success State */}
      {createdBusiness ? (
        <div className="rounded-2xl border border-emerald-200 bg-white p-6 sm:p-8 shadow-sm">
          <div className="flex items-center gap-3 text-emerald-600 mb-6">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 border border-emerald-100 flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6 text-emerald-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900">
                Business Successfully Registered!
              </h2>
              <p className="text-xs text-slate-500">
                The business record is now committed to the PostgreSQL database.
              </p>
            </div>
          </div>

          {/* Business ID Box */}
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200/80 mb-6">
            <span className="text-[11px] uppercase font-bold text-slate-400 tracking-wider block mb-1">
              Generated Business UUID
            </span>
            <div className="flex items-center justify-between gap-3">
              <code className="text-xs sm:text-sm font-mono font-semibold text-emerald-700 break-all select-all">
                {createdBusiness.id}
              </code>
              <button
                onClick={handleCopyId}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 transition-colors shadow-sm"
              >
                {copiedId ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                    <span className="text-emerald-600">Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Submitted Details Summary */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-8 text-xs">
            <div className="p-3 bg-slate-50/60 rounded-lg border border-slate-100">
              <span className="text-slate-400 block mb-0.5">Name</span>
              <span className="font-semibold text-slate-800">{createdBusiness.name}</span>
            </div>
            <div className="p-3 bg-slate-50/60 rounded-lg border border-slate-100">
              <span className="text-slate-400 block mb-0.5">Industry</span>
              <span className="font-semibold text-slate-800">{createdBusiness.industry}</span>
            </div>
            <div className="p-3 bg-slate-50/60 rounded-lg border border-slate-100">
              <span className="text-slate-400 block mb-0.5">Location</span>
              <span className="font-semibold text-slate-800">{createdBusiness.location}</span>
            </div>
            {createdBusiness.website && (
              <div className="p-3 bg-slate-50/60 rounded-lg border border-slate-100">
                <span className="text-slate-400 block mb-0.5">Website</span>
                <span className="font-semibold text-slate-800 truncate block">
                  {createdBusiness.website}
                </span>
              </div>
            )}
            {createdBusiness.business_age_years !== null && (
              <div className="p-3 bg-slate-50/60 rounded-lg border border-slate-100">
                <span className="text-slate-400 block mb-0.5">Age</span>
                <span className="font-semibold text-slate-800">
                  {createdBusiness.business_age_years} years
                </span>
              </div>
            )}
            {createdBusiness.revenue_range && (
              <div className="p-3 bg-slate-50/60 rounded-lg border border-slate-100">
                <span className="text-slate-400 block mb-0.5">Revenue</span>
                <span className="font-semibold text-slate-800">
                  {createdBusiness.revenue_range}
                </span>
              </div>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex flex-col sm:flex-row items-center gap-3">
            <button
              onClick={handleReset}
              className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-emerald-600 text-white font-semibold text-xs hover:bg-emerald-700 transition-colors shadow-sm"
            >
              Register Another Business
            </button>
            <Link
              href="/"
              className="w-full sm:w-auto px-5 py-2.5 rounded-xl border border-slate-200 text-slate-700 font-semibold text-xs text-center hover:bg-slate-50 transition-colors"
            >
              Return to Homepage
            </Link>
          </div>
        </div>
      ) : (
        /* Onboarding Form */
        <form
          onSubmit={handleSubmit}
          className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 shadow-sm space-y-6"
        >
          {/* Error Banner */}
          {errorMessage && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200/80 flex items-start gap-3 text-rose-800 text-xs">
              <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-bold block">Registration Error</span>
                <span>{errorMessage}</span>
              </div>
            </div>
          )}

          {/* Section 1: Core Required Identifiers */}
          <div className="space-y-4">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Building2 className="w-4 h-4 text-emerald-600" />
              <span>Core Business Profile (Required)</span>
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Business Name */}
              <div className="sm:col-span-2">
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Business Name <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="e.g., Apex Health Technologies Inc."
                  className={`w-full px-3.5 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 transition-all ${
                    clientErrors.name
                      ? "border-rose-300 focus:ring-rose-200 bg-rose-50/20"
                      : "border-slate-200 focus:ring-emerald-200 focus:border-emerald-500"
                  }`}
                />
                {clientErrors.name && (
                  <p className="text-[11px] text-rose-600 mt-1">{clientErrors.name}</p>
                )}
              </div>

              {/* Industry */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Industry / Sector <span className="text-rose-500">*</span>
                </label>
                <select
                  name="industry"
                  value={formData.industry}
                  onChange={handleChange}
                  className={`w-full px-3.5 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 transition-all bg-white ${
                    clientErrors.industry
                      ? "border-rose-300 focus:ring-rose-200"
                      : "border-slate-200 focus:ring-emerald-200 focus:border-emerald-500"
                  }`}
                >
                  <option value="">Select Industry...</option>
                  {COMMON_INDUSTRIES.map((ind) => (
                    <option key={ind} value={ind}>
                      {ind}
                    </option>
                  ))}
                </select>
                {formData.industry === "Other" && (
                  <input
                    type="text"
                    name="customIndustry"
                    value={formData.customIndustry}
                    onChange={handleChange}
                    placeholder="Specify your industry..."
                    className="w-full mt-2 px-3.5 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-200 focus:border-emerald-500"
                  />
                )}
                {clientErrors.industry && (
                  <p className="text-[11px] text-rose-600 mt-1">
                    {clientErrors.industry}
                  </p>
                )}
              </div>

              {/* Location */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Location (City, Country) <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleChange}
                  placeholder="e.g., Bengaluru, India or Austin, TX"
                  className={`w-full px-3.5 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 transition-all ${
                    clientErrors.location
                      ? "border-rose-300 focus:ring-rose-200"
                      : "border-slate-200 focus:ring-emerald-200 focus:border-emerald-500"
                  }`}
                />
                {clientErrors.location && (
                  <p className="text-[11px] text-rose-600 mt-1">
                    {clientErrors.location}
                  </p>
                )}
              </div>

              {/* Website */}
              <div className="sm:col-span-2">
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Official Website <span className="text-slate-400 font-normal">(Optional)</span>
                </label>
                <input
                  type="text"
                  name="website"
                  value={formData.website}
                  onChange={handleChange}
                  placeholder="https://example.com"
                  className={`w-full px-3.5 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 transition-all ${
                    clientErrors.website
                      ? "border-rose-300 focus:ring-rose-200"
                      : "border-slate-200 focus:ring-emerald-200 focus:border-emerald-500"
                  }`}
                />
                {clientErrors.website && (
                  <p className="text-[11px] text-rose-600 mt-1">{clientErrors.website}</p>
                )}
              </div>
            </div>
          </div>

          <hr className="border-slate-100" />

          {/* Section 2: Operational & Scale Metrics */}
          <div className="space-y-4">
            <div>
              <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                Operational & Financial Scale (Optional)
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Helps establish accurate benchmarking cohorts against comparable businesses.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Business Age */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Business Age (Years)
                </label>
                <input
                  type="number"
                  name="business_age_years"
                  min="0"
                  step="1"
                  value={formData.business_age_years}
                  onChange={handleChange}
                  placeholder="e.g., 5"
                  className={`w-full px-3.5 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 transition-all ${
                    clientErrors.business_age_years
                      ? "border-rose-300 focus:ring-rose-200"
                      : "border-slate-200 focus:ring-emerald-200 focus:border-emerald-500"
                  }`}
                />
                {clientErrors.business_age_years && (
                  <p className="text-[11px] text-rose-600 mt-1">
                    {clientErrors.business_age_years}
                  </p>
                )}
              </div>

              {/* Revenue Range */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Annual Revenue Range
                </label>
                <select
                  name="revenue_range"
                  value={formData.revenue_range}
                  onChange={handleChange}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-200 focus:border-emerald-500 bg-white"
                >
                  <option value="">Select Revenue Bracket...</option>
                  {REVENUE_RANGES.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </select>
              </div>

              {/* Employee Count */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Employee Count (Headcount)
                </label>
                <input
                  type="number"
                  name="employee_count"
                  min="0"
                  step="1"
                  value={formData.employee_count}
                  onChange={handleChange}
                  placeholder="e.g., 25"
                  className={`w-full px-3.5 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 transition-all ${
                    clientErrors.employee_count
                      ? "border-rose-300 focus:ring-rose-200"
                      : "border-slate-200 focus:ring-emerald-200 focus:border-emerald-500"
                  }`}
                />
                {clientErrors.employee_count && (
                  <p className="text-[11px] text-rose-600 mt-1">
                    {clientErrors.employee_count}
                  </p>
                )}
              </div>

              {/* Customer Count */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Active Customer Count
                </label>
                <input
                  type="number"
                  name="customer_count"
                  min="0"
                  step="1"
                  value={formData.customer_count}
                  onChange={handleChange}
                  placeholder="e.g., 1200"
                  className={`w-full px-3.5 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 transition-all ${
                    clientErrors.customer_count
                      ? "border-rose-300 focus:ring-rose-200"
                      : "border-slate-200 focus:ring-emerald-200 focus:border-emerald-500"
                  }`}
                />
                {clientErrors.customer_count && (
                  <p className="text-[11px] text-rose-600 mt-1">
                    {clientErrors.customer_count}
                  </p>
                )}
              </div>

              {/* Monthly Marketing Spend */}
              <div className="sm:col-span-2">
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Monthly Marketing Spend (₹ / $)
                </label>
                <input
                  type="number"
                  name="marketing_spend_monthly"
                  min="0"
                  step="0.01"
                  value={formData.marketing_spend_monthly}
                  onChange={handleChange}
                  placeholder="e.g., 50000"
                  className={`w-full px-3.5 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 transition-all ${
                    clientErrors.marketing_spend_monthly
                      ? "border-rose-300 focus:ring-rose-200"
                      : "border-slate-200 focus:ring-emerald-200 focus:border-emerald-500"
                  }`}
                />
                {clientErrors.marketing_spend_monthly && (
                  <p className="text-[11px] text-rose-600 mt-1">
                    {clientErrors.marketing_spend_monthly}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="pt-2">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm transition-colors shadow-sm disabled:opacity-60 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Submitting to Database...</span>
                </>
              ) : (
                <span>Register Business Record</span>
              )}
            </button>
            <p className="text-[11px] text-slate-400 text-center mt-2.5">
              Securely stored in PostgreSQL. Verified via FastAPI REST layer.
            </p>
          </div>
        </form>
      )}
    </div>
  );
}
