"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useRouter, useParams } from "next/navigation";
import Image from "next/image";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card } from "@/components/ui/Card";

export default function LoginPage() {
  const t = useTranslations("auth");
  const router = useRouter();
  const params = useParams<{ locale: string }>();
  const locale = params?.locale ?? "fr";
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // MFA step state
  const [mfaUserId, setMfaUserId] = useState<string | null>(null);
  const [totpCode, setTotpCode] = useState("");
  const [mfaError, setMfaError] = useState("");
  const [mfaSubmitting, setMfaSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const result = await login(email, password);
      if (result.type === "success") {
        router.push(`/${locale}/dashboard`);
      } else if (result.type === "mfa_required") {
        setMfaUserId(result.userId);
      }
    } catch {
      setError(t("invalidCredentials"));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleMfaSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMfaError("");
    setMfaSubmitting(true);
    try {
      const { api } = await import("@/lib/api");
      await api<{ access_token: string; refresh_token: string }>("/auth/mfa/verify", {
        method: "POST",
        body: JSON.stringify({ user_id: mfaUserId, code: totpCode }),
      });
      router.push(`/${locale}/dashboard`);
    } catch {
      setMfaError(t("invalidMfaCode"));
    } finally {
      setMfaSubmitting(false);
    }
  }

  if (mfaUserId !== null) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
        <Card className="w-full max-w-sm">
          <h1 className="text-xl font-semibold text-slate-800 mb-1">{t("mfaTitle")}</h1>
          <p className="text-sm text-slate-500 mb-6">{t("mfaDescription")}</p>
          <form onSubmit={handleMfaSubmit} className="flex flex-col gap-4">
            <Input
              label={t("totpCode")}
              type="text"
              inputMode="numeric"
              pattern="[0-9]{6}"
              maxLength={6}
              placeholder={t("totpPlaceholder")}
              value={totpCode}
              onChange={(e) => setTotpCode(e.target.value)}
              error={mfaError}
              required
              autoFocus
            />
            <Button type="submit" loading={mfaSubmitting} disabled={mfaSubmitting} className="w-full">
              {t("verifyCode")}
            </Button>
          </form>
        </Card>
      </main>
    );
  }

  return (
    <main className="min-h-screen flex bg-slate-50">
      {/* Hero image panel — hidden on small screens */}
      <div className="hidden md:flex md:w-1/2 relative bg-[#0d9488]">
        <Image
          src="https://images.unsplash.com/photo-1584820927498-cfe5211fd8bf?w=1200&q=80"
          alt="Tropical medicine clinic — healthcare professionals at work"
          fill
          className="object-cover opacity-30"
          priority
        />
        <div className="relative z-10 flex flex-col justify-end p-12 text-white">
          <h2 className="text-3xl font-bold">Trop-Med</h2>
          <p className="mt-2 text-teal-100 text-sm max-w-xs">
            Clinical platform for tropical medicine — connecting care across borders.
          </p>
        </div>
      </div>

      {/* Login form panel */}
      <div className="flex flex-1 items-center justify-center px-4">
        <Card className="w-full max-w-sm">
          <h1 className="text-2xl font-bold text-[#0d9488] mb-6">Trop-Med</h1>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Input
              label={t("email")}
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
            <Input
              label={t("password")}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              error={error}
              required
              autoComplete="current-password"
            />
            <Button type="submit" loading={submitting} disabled={submitting} className="w-full">
              {t("signIn")}
            </Button>
          </form>
        </Card>
      </div>
    </main>
  );
}
