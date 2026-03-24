"use client";

import { useTranslations } from "next-intl";
import { useParams } from "next/navigation";
import { Shell } from "@/components/ui/Shell";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";

export default function NotificationsPage() {
  const tc = useTranslations("common");
  const params = useParams<{ locale: string }>();
  const locale = params?.locale ?? "fr";

  const navItems = [
    { label: tc("dashboard"), href: `/${locale}/dashboard` },
    { label: tc("patients"), href: `/${locale}/patients` },
    { label: tc("chat"), href: `/${locale}/chat` },
    { label: tc("surveillance"), href: `/${locale}/surveillance` },
    { label: tc("notifications"), href: `/${locale}/notifications` },
    { label: tc("settings"), href: `/${locale}/settings` },
  ];

  return (
    <ErrorBoundary>
      <Shell navItems={navItems}>
        <div className="space-y-4">
          <h1 className="text-xl font-semibold text-slate-800">{tc("notifications")}</h1>
          <p className="text-slate-500 text-sm">Coming soon.</p>
        </div>
      </Shell>
    </ErrorBoundary>
  );
}
