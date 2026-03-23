"use client";

import { useEffect, useState, useCallback } from "react";
import { useTranslations } from "next-intl";
import { useParams } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { patientsApi, ApiError } from "@/lib/api";
import type { Patient } from "@/lib/api";
import { Shell } from "@/components/ui/Shell";
import { Spinner } from "@/components/ui/Spinner";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";

function PatientRowSkeleton() {
  return (
    <tr>
      {[...Array(4)].map((_, i) => (
        <td key={i} className="px-4 py-3">
          <div className="h-4 bg-slate-200 rounded animate-pulse" />
        </td>
      ))}
    </tr>
  );
}

export default function PatientsPage() {
  const t = useTranslations("patient");
  const tc = useTranslations("common");
  const params = useParams<{ locale: string }>();
  const locale = params?.locale ?? "fr";
  const { token } = useAuth();

  const [patients, setPatients] = useState<Patient[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isNetworkError, setIsNetworkError] = useState(false);

  const navItems = [
    { label: tc("dashboard"), href: `/${locale}/dashboard` },
    { label: tc("patients"), href: `/${locale}/patients` },
    { label: tc("chat"), href: `/${locale}/chat` },
    { label: tc("surveillance"), href: `/${locale}/surveillance` },
    { label: tc("notifications"), href: `/${locale}/notifications` },
    { label: tc("settings"), href: `/${locale}/settings` },
  ];

  const fetchPatients = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    setIsNetworkError(false);
    const controller = new AbortController();
    try {
      const data = await patientsApi.list({ search: query }, token, controller.signal);
      setPatients(data.items);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(tc("error"));
      } else if (err instanceof Error && err.name !== "AbortError") {
        setIsNetworkError(true);
        setError(tc("networkError"));
      }
    } finally {
      setLoading(false);
    }
    return () => controller.abort();
  }, [token, query, tc]);

  useEffect(() => {
    fetchPatients();
  }, [fetchPatients]);

  return (
    <ErrorBoundary>
      <Shell navItems={navItems}>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-semibold text-slate-800">{tc("patients")}</h1>
          </div>

          <input
            placeholder={tc("search")}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full max-w-sm px-3 py-2 border border-slate-200 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#0d9488]"
          />

          {/* Error banner */}
          {error && (
            <div className="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-700">
              <span>{error}</span>
              {isNetworkError && (
                <button
                  onClick={fetchPatients}
                  className="ml-4 px-3 py-1 text-xs font-medium text-white bg-red-600 rounded hover:bg-red-700"
                >
                  {tc("retry")}
                </button>
              )}
            </div>
          )}

          <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-100">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-slate-600">{t("givenName")}</th>
                  <th className="px-4 py-3 text-left font-medium text-slate-600">{t("familyName")}</th>
                  <th className="px-4 py-3 text-left font-medium text-slate-600">{t("dateOfBirth")}</th>
                  <th className="px-4 py-3 text-left font-medium text-slate-600">{t("gender")}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {loading ? (
                  <>
                    <PatientRowSkeleton />
                    <PatientRowSkeleton />
                    <PatientRowSkeleton />
                  </>
                ) : patients.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-4 py-10 text-center text-slate-400">
                      {t("noPatients") ?? "No patients found."}
                    </td>
                  </tr>
                ) : (
                  patients.map((p) => (
                    <tr key={p.id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-4 py-3 text-slate-700">{p.full_name.split(" ")[0]}</td>
                      <td className="px-4 py-3 text-slate-700">{p.full_name.split(" ").slice(1).join(" ")}</td>
                      <td className="px-4 py-3 text-slate-500">{p.date_of_birth ?? "—"}</td>
                      <td className="px-4 py-3 text-slate-500">{p.gender ?? "—"}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {loading && (
            <div className="flex justify-center py-4">
              <Spinner size="md" className="text-[#0d9488]" />
            </div>
          )}
        </div>
      </Shell>
    </ErrorBoundary>
  );
}
