"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useRouter, useParams } from "next/navigation";
import Image from "next/image";
import { useAuth } from "@/hooks/useAuth";
import { notificationsApi } from "@/lib/api";
import { Shell } from "@/components/ui/Shell";
import { Badge } from "@/components/ui/Badge";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import type { Role } from "@/components/ui/types";

export default function DashboardPage() {
  const t = useTranslations("common");
  const router = useRouter();
  const params = useParams<{ locale: string }>();
  const locale = params?.locale ?? "fr";
  const { user, logout, token } = useAuth();

  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (!token) return;
    const controller = new AbortController();
    notificationsApi
      .list(token, controller.signal)
      .then((data) => setUnreadCount(data.unread_count))
      .catch(() => {});
    return () => controller.abort();
  }, [token]);

  function handleLogout() {
    logout();
    router.push(`/${locale}/login`);
  }

  const navItems = [
    { label: t("dashboard"), href: `/${locale}/dashboard` },
    { label: t("patients"), href: `/${locale}/patients` },
    { label: t("chat"), href: `/${locale}/chat` },
    { label: t("surveillance"), href: `/${locale}/surveillance` },
    {
      label: t("notifications"),
      href: `/${locale}/notifications`,
      badge: unreadCount > 0 ? unreadCount : undefined,
    },
    { label: t("settings"), href: `/${locale}/settings` },
  ];

  const headerContent = (
    <div className="flex items-center justify-between w-full">
      <span className="text-sm font-medium text-slate-700">
        {user?.sub ?? ""}
      </span>
      <div className="flex items-center gap-3">
        {user?.role && <Badge role={user.role as Role} />}
        <button
          onClick={handleLogout}
          className="text-sm text-slate-500 hover:text-[#dc2626] transition-colors"
        >
          {t("logout")}
        </button>
      </div>
    </div>
  );

  return (
    <ErrorBoundary>
      <Shell navItems={navItems} headerContent={headerContent}>
        <div className="space-y-6">
          {/* Welcome banner with image */}
          <div className="relative rounded-xl overflow-hidden bg-[#0d9488] text-white">
            <Image
              src="https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=1200&q=80"
              alt="Medical professionals in a tropical medicine clinic"
              width={1200}
              height={300}
              className="absolute inset-0 w-full h-full object-cover opacity-20"
              priority
            />
            <div className="relative px-8 py-10">
              <h1 className="text-2xl font-bold">
                {t("welcome")}{user?.sub ? `, ${user.sub}` : ""}
              </h1>
              <p className="mt-1 text-teal-100 text-sm">{t("appName")} — v1.0</p>
            </div>
          </div>

          {/* Quick-access cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {navItems.slice(1).map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="block p-5 bg-white rounded-xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-700">{item.label}</span>
                  {item.badge != null && item.badge > 0 && (
                    <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-[#0d9488] rounded-full">
                      {item.badge}
                    </span>
                  )}
                </div>
              </a>
            ))}
          </div>
        </div>
      </Shell>
    </ErrorBoundary>
  );
}
