"use client";

import { usePathname, useRouter } from "next/navigation";

const LOCALES = [
  { code: "fr", label: "Français" },
  { code: "en", label: "English" },
];

export function LocaleSwitcher() {
  const pathname = usePathname();
  const router = useRouter();
  const currentLocale = pathname.split("/")[1] || "fr";

  function switchLocale(locale: string) {
    const newPath = pathname.replace(`/${currentLocale}`, `/${locale}`);
    router.push(newPath);
  }

  return (
    <select
      value={currentLocale}
      onChange={(e) => switchLocale(e.target.value)}
      style={{ padding: 4 }}
    >
      {LOCALES.map((l) => (
        <option key={l.code} value={l.code}>
          {l.label}
        </option>
      ))}
    </select>
  );
}
