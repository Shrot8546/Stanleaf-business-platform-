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
  ClipboardList,
  CheckCheck,
  HelpCircle,
} from "lucide-react";
import {
  createBusiness,
  fetchQuestionnaire,
  submitQuestionnaire,
  Business,
  QuestionnaireDefinition,
  QuestionItem,
  QuestionnaireSubmissionResult,
} from "@/lib/api";

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
  "Restaurant",
  "E-Commerce & D2C",
  "Software & SaaS",
  "FinTech & Financial Services",
  "Healthcare & MedTech",
  "Manufacturing & Industrial",
  "Logistics & Supply Chain",
  "Retail & Consumer Goods",
  "Other",
];

export default function OnboardingPage() {
  // Step navigation: 1 = Business Info, 2 = Questionnaire, 3 = Complete
  const [currentStep, setCurrentStep] = useState<1 | 2 | 3>(1);

  // Step 1: Business Profile Form State
  const [businessForm, setBusinessForm] = useState({
    name: "",
    industry: "Restaurant",
    customIndustry: "",
    location: "",
    website: "",
    business_age_years: "",
    revenue_range: "",
    employee_count: "",
    customer_count: "",
    marketing_spend_monthly: "",
  });

  const [loadingBusiness, setLoadingBusiness] = useState(false);
  const [businessErrors, setBusinessErrors] = useState<Record<string, string>>({});
  const [businessErrorBanner, setBusinessErrorBanner] = useState<string | null>(null);

  // Created Business metadata
  const [createdBusiness, setCreatedBusiness] = useState<Business | null>(null);

  // Step 2: Questionnaire State (Fetched dynamically from backend)
  const [questionnaireDef, setQuestionnaireDef] = useState<QuestionnaireDefinition | null>(null);
  const [questionnaireAnswers, setQuestionnaireAnswers] = useState<Record<string, any>>({});
  const [questionnaireErrors, setQuestionnaireErrors] = useState<Record<string, string>>({});
  const [loadingQuestionnaire, setLoadingQuestionnaire] = useState(false);
  const [submittingAnswers, setSubmittingAnswers] = useState(false);
  const [questionnaireErrorBanner, setQuestionnaireErrorBanner] = useState<string | null>(null);

  // Step 3: Final Submission Result
  const [submissionResult, setSubmissionResult] = useState<QuestionnaireSubmissionResult | null>(null);
  const [copiedId, setCopiedId] = useState(false);

  // --------------------------------------------------------------------------
  // STEP 1: Handlers & Validation
  // --------------------------------------------------------------------------
  const validateBusinessForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!businessForm.name.trim()) {
      errors.name = "Business name is required.";
    }

    const effectiveIndustry =
      businessForm.industry === "Other"
        ? businessForm.customIndustry.trim()
        : businessForm.industry.trim();
    if (!effectiveIndustry) {
      errors.industry = "Industry sector is required.";
    }

    if (!businessForm.location.trim()) {
      errors.location = "Operating location is required.";
    }

    if (businessForm.website.trim()) {
      const urlPattern =
        /^(https?:\/\/)?([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(:\d{1,5})?(\/[^\s]*)?$/i;
      if (!urlPattern.test(businessForm.website.trim())) {
        errors.website = "Enter a valid website URL (e.g. https://example.com).";
      }
    }

    if (businessForm.business_age_years !== "") {
      const val = Number(businessForm.business_age_years);
      if (isNaN(val) || val < 0) {
        errors.business_age_years = "Business age must be >= 0.";
      }
    }

    if (businessForm.employee_count !== "") {
      const val = Number(businessForm.employee_count);
      if (isNaN(val) || val < 0) {
        errors.employee_count = "Employee count must be >= 0.";
      }
    }

    if (businessForm.customer_count !== "") {
      const val = Number(businessForm.customer_count);
      if (isNaN(val) || val < 0) {
        errors.customer_count = "Customer count must be >= 0.";
      }
    }

    if (businessForm.marketing_spend_monthly !== "") {
      const val = Number(businessForm.marketing_spend_monthly);
      if (isNaN(val) || val < 0) {
        errors.marketing_spend_monthly = "Marketing spend must be >= 0.";
      }
    }

    setBusinessErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleBusinessChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setBusinessForm((prev) => ({ ...prev, [name]: value }));
    if (businessErrors[name]) {
      setBusinessErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  const handleBusinessSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusinessErrorBanner(null);

    if (!validateBusinessForm()) return;

    setLoadingBusiness(true);

    try {
      const effectiveIndustry =
        businessForm.industry === "Other"
          ? businessForm.customIndustry.trim()
          : businessForm.industry.trim();

      const payload = {
        name: businessForm.name.trim(),
        industry: effectiveIndustry,
        location: businessForm.location.trim(),
        website: businessForm.website.trim() || undefined,
        business_age_years:
          businessForm.business_age_years !== ""
            ? parseInt(businessForm.business_age_years, 10)
            : undefined,
        revenue_range: businessForm.revenue_range.trim() || undefined,
        employee_count:
          businessForm.employee_count !== ""
            ? parseInt(businessForm.employee_count, 10)
            : undefined,
        customer_count:
          businessForm.customer_count !== ""
            ? parseInt(businessForm.customer_count, 10)
            : undefined,
        marketing_spend_monthly:
          businessForm.marketing_spend_monthly !== ""
            ? parseFloat(businessForm.marketing_spend_monthly)
            : undefined,
      };

      const created = await createBusiness(payload);
      setCreatedBusiness(created);

      // Now fetch the questionnaire definition for this industry
      setLoadingQuestionnaire(true);
      try {
        const qDef = await fetchQuestionnaire(created.industry);
        setQuestionnaireDef(qDef);

        // Prepopulate answers map with defaults or empty strings
        const initialAnswers: Record<string, any> = {};
        qDef.questions.forEach((q) => {
          initialAnswers[q.id] = q.data_type === "boolean" ? false : "";
        });
        setQuestionnaireAnswers(initialAnswers);
        setCurrentStep(2);
      } catch (qErr: unknown) {
        // If questionnaire is not available for this industry yet, transition to completed profile
        console.warn("Questionnaire definition not available:", qErr);
        setQuestionnaireDef(null);
        setCurrentStep(3);
      } finally {
        setLoadingQuestionnaire(false);
      }
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Failed to register business record.";
      setBusinessErrorBanner(msg);
    } finally {
      setLoadingBusiness(false);
    }
  };

  // --------------------------------------------------------------------------
  // STEP 2: Handlers & Validation
  // --------------------------------------------------------------------------
  const handleAnswerChange = (questionId: string, val: any) => {
    setQuestionnaireAnswers((prev) => ({ ...prev, [questionId]: val }));
    if (questionnaireErrors[questionId]) {
      setQuestionnaireErrors((prev) => ({ ...prev, [questionId]: "" }));
    }
  };

  const validateQuestionnaire = (): boolean => {
    if (!questionnaireDef) return true;
    const errors: Record<string, string> = {};

    for (const q of questionnaireDef.questions) {
      const val = questionnaireAnswers[q.id];

      // Required check
      if (q.required) {
        if (val === undefined || val === null || val === "") {
          errors[q.id] = "This question is required.";
          continue;
        }
      }

      // If value is filled, validate types and boundaries
      if (val !== undefined && val !== null && val !== "") {
        if (["integer", "decimal", "currency", "percentage"].includes(q.data_type)) {
          const num = Number(val);
          if (isNaN(num)) {
            errors[q.id] = "Please enter a valid numerical value.";
            continue;
          }
          if (q.data_type === "integer" && !Number.isInteger(num)) {
            errors[q.id] = "Value must be an integer.";
            continue;
          }
          if (q.min_value !== null && q.min_value !== undefined && num < q.min_value) {
            errors[q.id] = `Value cannot be less than ${q.min_value}.`;
            continue;
          }
          if (q.max_value !== null && q.max_value !== undefined && num > q.max_value) {
            errors[q.id] = `Value cannot exceed ${q.max_value}.`;
            continue;
          }
        }
      }
    }

    setQuestionnaireErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleQuestionnaireSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setQuestionnaireErrorBanner(null);

    if (!createdBusiness?.id) {
      setQuestionnaireErrorBanner("Missing active business ID. Please restart onboarding.");
      return;
    }

    if (!validateQuestionnaire()) {
      setQuestionnaireErrorBanner("Please review the highlighted errors before submitting.");
      return;
    }

    setSubmittingAnswers(true);

    try {
      const formattedResponses = Object.entries(questionnaireAnswers)
        .filter(([_, value]) => value !== undefined && value !== null && value !== "")
        .map(([question_id, value]) => ({
          question_id,
          value,
        }));

      const res = await submitQuestionnaire(createdBusiness.id, formattedResponses);
      setSubmissionResult(res);
      setCurrentStep(3);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Failed to submit questionnaire responses.";
      setQuestionnaireErrorBanner(msg);
    } finally {
      setSubmittingAnswers(false);
    }
  };

  const handleCopyId = () => {
    const idToCopy = createdBusiness?.id || submissionResult?.business_id;
    if (idToCopy) {
      navigator.clipboard.writeText(idToCopy);
      setCopiedId(true);
      setTimeout(() => setCopiedId(false), 2500);
    }
  };

  const handleReset = () => {
    setCurrentStep(1);
    setBusinessForm({
      name: "",
      industry: "Restaurant",
      customIndustry: "",
      location: "",
      website: "",
      business_age_years: "",
      revenue_range: "",
      employee_count: "",
      customer_count: "",
      marketing_spend_monthly: "",
    });
    setBusinessErrors({});
    setBusinessErrorBanner(null);
    setCreatedBusiness(null);
    setQuestionnaireDef(null);
    setQuestionnaireAnswers({});
    setQuestionnaireErrors({});
    setSubmissionResult(null);
  };

  // Group questions by category for clean visual layout
  const groupedQuestions = questionnaireDef
    ? questionnaireDef.questions.reduce((acc, q) => {
        if (!acc[q.category]) acc[q.category] = [];
        acc[q.category].push(q);
        return acc;
      }, {} as Record<string, QuestionItem[]>)
    : {};

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Back button */}
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 transition-colors mb-6"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Home</span>
      </Link>

      {/* Progress Steps Header */}
      <div className="mb-10">
        <div className="flex items-center justify-between border-b border-slate-200 pb-5">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/80 mb-2">
              <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
              <span>Step 3 — Industry-Specific Questionnaire Engine</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              {currentStep === 1 && "Step 1: Business Profile"}
              {currentStep === 2 && `Step 2: ${questionnaireDef?.title || "Industry Questionnaire"}`}
              {currentStep === 3 && "Step 3: Verification & Record Created"}
            </h1>
          </div>

          {/* Stepper Indicator */}
          <div className="hidden sm:flex items-center gap-2 text-xs font-medium">
            <span
              className={`px-3 py-1 rounded-full flex items-center gap-1.5 ${
                currentStep === 1
                  ? "bg-emerald-600 text-white font-bold shadow-sm"
                  : "bg-emerald-100 text-emerald-800"
              }`}
            >
              <Building2 className="w-3.5 h-3.5" /> Profile
            </span>
            <span className="text-slate-300">→</span>
            <span
              className={`px-3 py-1 rounded-full flex items-center gap-1.5 ${
                currentStep === 2
                  ? "bg-emerald-600 text-white font-bold shadow-sm"
                  : currentStep > 2
                  ? "bg-emerald-100 text-emerald-800"
                  : "bg-slate-100 text-slate-400"
              }`}
            >
              <ClipboardList className="w-3.5 h-3.5" /> Diagnostic
            </span>
            <span className="text-slate-300">→</span>
            <span
              className={`px-3 py-1 rounded-full flex items-center gap-1.5 ${
                currentStep === 3
                  ? "bg-emerald-600 text-white font-bold shadow-sm"
                  : "bg-slate-100 text-slate-400"
              }`}
            >
              <CheckCheck className="w-3.5 h-3.5" /> Verified
            </span>
          </div>
        </div>
      </div>

      {/* ==================================================================== */}
      {/* STEP 1: BUSINESS PROFILE FORM                                        */}
      {/* ==================================================================== */}
      {currentStep === 1 && (
        <form
          onSubmit={handleBusinessSubmit}
          className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 shadow-sm space-y-6"
        >
          {businessErrorBanner && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200/80 flex items-start gap-3 text-rose-800 text-xs">
              <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-bold block">Registration Error</span>
                <span>{businessErrorBanner}</span>
              </div>
            </div>
          )}

          <div>
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2 mb-1">
              <Building2 className="w-4 h-4 text-emerald-600" />
              <span>Core Business Profile (Required)</span>
            </h2>
            <p className="text-xs text-slate-500">
              Select your industry to load the appropriate diagnostic questions in Step 2.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Business Name */}
            <div className="sm:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Business Name <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                name="name"
                value={businessForm.name}
                onChange={handleBusinessChange}
                placeholder="e.g. Bella Cucina Italian Bistro"
                className={`w-full px-3.5 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 transition-all ${
                  businessErrors.name
                    ? "border-rose-300 focus:ring-rose-200 bg-rose-50/20"
                    : "border-slate-200 focus:ring-emerald-200 focus:border-emerald-500"
                }`}
              />
              {businessErrors.name && (
                <p className="text-[11px] text-rose-600 mt-1">{businessErrors.name}</p>
              )}
            </div>

            {/* Industry Selector */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Industry Sector <span className="text-rose-500">*</span>
              </label>
              <select
                name="industry"
                value={businessForm.industry}
                onChange={handleBusinessChange}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-200 focus:border-emerald-500 bg-white"
              >
                {COMMON_INDUSTRIES.map((ind) => (
                  <option key={ind} value={ind}>
                    {ind} {ind === "Restaurant" || ind === "E-Commerce & D2C" ? "(Full Questionnaire Available)" : ""}
                  </option>
                ))}
              </select>
              {businessForm.industry === "Other" && (
                <input
                  type="text"
                  name="customIndustry"
                  value={businessForm.customIndustry}
                  onChange={handleBusinessChange}
                  placeholder="Specify industry..."
                  className="w-full mt-2 px-3.5 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-200 focus:border-emerald-500"
                />
              )}
              {businessErrors.industry && (
                <p className="text-[11px] text-rose-600 mt-1">{businessErrors.industry}</p>
              )}
            </div>

            {/* Location */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Operating Location <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                name="location"
                value={businessForm.location}
                onChange={handleBusinessChange}
                placeholder="e.g. Chicago, IL or Bengaluru, India"
                className={`w-full px-3.5 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 transition-all ${
                  businessErrors.location
                    ? "border-rose-300 focus:ring-rose-200"
                    : "border-slate-200 focus:ring-emerald-200 focus:border-emerald-500"
                }`}
              />
              {businessErrors.location && (
                <p className="text-[11px] text-rose-600 mt-1">{businessErrors.location}</p>
              )}
            </div>

            {/* Website */}
            <div className="sm:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Website URL <span className="text-slate-400 font-normal">(Optional)</span>
              </label>
              <input
                type="text"
                name="website"
                value={businessForm.website}
                onChange={handleBusinessChange}
                placeholder="https://bistrobella.com"
                className={`w-full px-3.5 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 transition-all ${
                  businessErrors.website
                    ? "border-rose-300 focus:ring-rose-200"
                    : "border-slate-200 focus:ring-emerald-200 focus:border-emerald-500"
                }`}
              />
              {businessErrors.website && (
                <p className="text-[11px] text-rose-600 mt-1">{businessErrors.website}</p>
              )}
            </div>
          </div>

          <hr className="border-slate-100" />

          {/* Section 2: Optional Scale Indicators */}
          <div className="space-y-4">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
              Operational Scale Indicators (Optional)
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Business Age (Years)
                </label>
                <input
                  type="number"
                  name="business_age_years"
                  min="0"
                  step="1"
                  value={businessForm.business_age_years}
                  onChange={handleBusinessChange}
                  placeholder="e.g. 3"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-200 focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Revenue Bracket
                </label>
                <select
                  name="revenue_range"
                  value={businessForm.revenue_range}
                  onChange={handleBusinessChange}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-200 focus:border-emerald-500 bg-white"
                >
                  <option value="">Select Bracket...</option>
                  {REVENUE_RANGES.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Employee Count
                </label>
                <input
                  type="number"
                  name="employee_count"
                  min="0"
                  step="1"
                  value={businessForm.employee_count}
                  onChange={handleBusinessChange}
                  placeholder="e.g. 15"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-200 focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Monthly Marketing Spend
                </label>
                <input
                  type="number"
                  name="marketing_spend_monthly"
                  min="0"
                  step="0.01"
                  value={businessForm.marketing_spend_monthly}
                  onChange={handleBusinessChange}
                  placeholder="e.g. 25000"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-200 focus:border-emerald-500"
                />
              </div>
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={loadingBusiness || loadingQuestionnaire}
              className="w-full py-3 px-5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm transition-colors shadow-sm disabled:opacity-60 flex items-center justify-center gap-2"
            >
              {loadingBusiness || loadingQuestionnaire ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Registering & Loading Questionnaire...</span>
                </>
              ) : (
                <span>Continue to Step 2: Industry Questionnaire →</span>
              )}
            </button>
          </div>
        </form>
      )}

      {/* ==================================================================== */}
      {/* STEP 2: DYNAMIC INDUSTRY QUESTIONNAIRE FORM                          */}
      {/* ==================================================================== */}
      {currentStep === 2 && questionnaireDef && (
        <form
          onSubmit={handleQuestionnaireSubmit}
          className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 shadow-sm space-y-8"
        >
          {/* Business summary header banner */}
          <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
            <div>
              <span className="font-semibold text-slate-900 block text-sm">
                {createdBusiness?.name}
              </span>
              <span className="text-slate-500">
                Industry: <strong className="text-emerald-700">{createdBusiness?.industry}</strong> • Location: {createdBusiness?.location}
              </span>
            </div>
            <span className="px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 font-mono text-[11px] font-semibold">
              ID: {createdBusiness?.id.slice(0, 8)}...
            </span>
          </div>

          {questionnaireErrorBanner && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200/80 flex items-start gap-3 text-rose-800 text-xs">
              <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-bold block">Validation Error</span>
                <span>{questionnaireErrorBanner}</span>
              </div>
            </div>
          )}

          <div>
            <p className="text-xs text-slate-500 leading-relaxed">
              {questionnaireDef.description}
            </p>
          </div>

          {/* Grouped Questions by Category */}
          {Object.entries(groupedQuestions).map(([category, questions]) => (
            <div key={category} className="space-y-4 pt-2">
              <div className="border-b border-slate-200 pb-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                  {category} Metrics
                </h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                {questions.map((q) => (
                  <div key={q.id} className="space-y-1.5">
                    <label className="block text-xs font-semibold text-slate-800">
                      {q.question_text}{" "}
                      {q.required ? (
                        <span className="text-rose-500">*</span>
                      ) : (
                        <span className="text-slate-400 font-normal">(Optional)</span>
                      )}
                    </label>

                    {q.description && (
                      <p className="text-[11px] text-slate-400 leading-snug flex items-center gap-1">
                        <HelpCircle className="w-3 h-3 flex-shrink-0 text-slate-300" />
                        <span>{q.description}</span>
                      </p>
                    )}

                    {/* Input Element according to data_type */}
                    <div className="relative mt-1">
                      {q.data_type === "select" ? (
                        <select
                          value={questionnaireAnswers[q.id] || ""}
                          onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                          className={`w-full px-3.5 py-2.5 rounded-xl border text-sm bg-white focus:outline-none focus:ring-2 transition-all ${
                            questionnaireErrors[q.id]
                              ? "border-rose-300 focus:ring-rose-200"
                              : "border-slate-200 focus:ring-emerald-200 focus:border-emerald-500"
                          }`}
                        >
                          <option value="">Select option...</option>
                          {q.options?.map((opt) => (
                            <option key={opt} value={opt}>
                              {opt}
                            </option>
                          ))}
                        </select>
                      ) : q.data_type === "boolean" ? (
                        <div className="flex items-center gap-4 py-2">
                          <label className="flex items-center gap-2 text-xs text-slate-700 cursor-pointer">
                            <input
                              type="radio"
                              name={q.id}
                              checked={questionnaireAnswers[q.id] === true}
                              onChange={() => handleAnswerChange(q.id, true)}
                              className="text-emerald-600 focus:ring-emerald-500"
                            />
                            <span>Yes</span>
                          </label>
                          <label className="flex items-center gap-2 text-xs text-slate-700 cursor-pointer">
                            <input
                              type="radio"
                              name={q.id}
                              checked={questionnaireAnswers[q.id] === false}
                              onChange={() => handleAnswerChange(q.id, false)}
                              className="text-emerald-600 focus:ring-emerald-500"
                            />
                            <span>No</span>
                          </label>
                        </div>
                      ) : (
                        <div className="relative flex items-center">
                          <input
                            type={["integer", "decimal", "currency", "percentage"].includes(q.data_type) ? "number" : "text"}
                            step={q.data_type === "integer" ? "1" : "any"}
                            min={q.min_value !== null ? q.min_value : undefined}
                            max={q.max_value !== null ? q.max_value : undefined}
                            value={questionnaireAnswers[q.id] ?? ""}
                            onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                            placeholder={
                              q.data_type === "percentage"
                                ? "e.g. 45"
                                : q.data_type === "decimal"
                                ? "e.g. 4.5"
                                : "Enter value..."
                            }
                            className={`w-full px-3.5 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 transition-all ${
                              q.unit ? "pr-14" : ""
                            } ${
                              questionnaireErrors[q.id]
                                ? "border-rose-300 focus:ring-rose-200 bg-rose-50/20"
                                : "border-slate-200 focus:ring-emerald-200 focus:border-emerald-500"
                            }`}
                          />
                          {q.unit && (
                            <span className="absolute right-3 text-xs font-semibold text-slate-400 select-none">
                              {q.unit}
                            </span>
                          )}
                        </div>
                      )}
                    </div>

                    {questionnaireErrors[q.id] && (
                      <p className="text-[11px] text-rose-600 mt-0.5">
                        {questionnaireErrors[q.id]}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}

          <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-3">
            <button
              type="button"
              onClick={() => setCurrentStep(1)}
              className="text-xs font-semibold text-slate-500 hover:text-slate-900 transition-colors"
            >
              ← Edit Business Information
            </button>

            <button
              type="submit"
              disabled={submittingAnswers}
              className="w-full sm:w-auto py-3 px-6 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm transition-colors shadow-sm disabled:opacity-60 flex items-center justify-center gap-2"
            >
              {submittingAnswers ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Validating & Storing in PostgreSQL...</span>
                </>
              ) : (
                <span>Complete Questionnaire & Save Record →</span>
              )}
            </button>
          </div>
        </form>
      )}

      {/* ==================================================================== */}
      {/* STEP 3: SUCCESS & CONFIRMATION STATE                                 */}
      {/* ==================================================================== */}
      {currentStep === 3 && (
        <div className="rounded-2xl border border-emerald-200 bg-white p-6 sm:p-8 shadow-sm space-y-6">
          <div className="flex items-center gap-3 text-emerald-600">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 border border-emerald-100 flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6 text-emerald-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900">
                Business Onboarding & Diagnostic Complete!
              </h2>
              <p className="text-xs text-slate-500">
                Data records committed and verified in PostgreSQL for downstream Data Science processing.
              </p>
            </div>
          </div>

          {/* Business ID Box */}
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200/80">
            <span className="text-[11px] uppercase font-bold text-slate-400 tracking-wider block mb-1">
              Registered Business UUID
            </span>
            <div className="flex items-center justify-between gap-3">
              <code className="text-xs sm:text-sm font-mono font-semibold text-emerald-700 break-all select-all">
                {createdBusiness?.id}
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

          {/* Metrics summary */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="p-3 bg-slate-50/60 rounded-lg border border-slate-100">
              <span className="text-slate-400 block mb-0.5">Business Name</span>
              <span className="font-semibold text-slate-800">{createdBusiness?.name}</span>
            </div>
            <div className="p-3 bg-slate-50/60 rounded-lg border border-slate-100">
              <span className="text-slate-400 block mb-0.5">Industry Sector</span>
              <span className="font-semibold text-slate-800">{createdBusiness?.industry}</span>
            </div>
            <div className="p-3 bg-slate-50/60 rounded-lg border border-slate-100">
              <span className="text-slate-400 block mb-0.5">Responses Recorded</span>
              <span className="font-semibold text-emerald-700">
                {submissionResult ? `${submissionResult.responses_count} Verified Metrics` : "Profile Saved"}
              </span>
            </div>
            <div className="p-3 bg-slate-50/60 rounded-lg border border-slate-100">
              <span className="text-slate-400 block mb-0.5">Data Science Layer</span>
              <span className="font-semibold text-slate-700">Ready for Ingestion</span>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
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
      )}
    </div>
  );
}
