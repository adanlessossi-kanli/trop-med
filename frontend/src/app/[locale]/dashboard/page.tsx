"use client";

import { useTranslations } from "next-intl";

export default function DashboardPage() {
  const t = useTranslations("common");

  return (
    <main style={{ padding: 24 }}>
      <h1>{t("dashboard")}</h1>
      <nav style={{ display: "flex", gap: 16, marginBottom: 24 }}>
        <a href="patients">{t("patients")}</a>
        <a href="chat">{t("chat")}</a>
        <a href="#">{t("surveillance")}</a>
        <a href="#">{t("notifications")}</a>
      </nav>
      <p>{t("appName")} — v1.0</p>
    </main>
  );
}
