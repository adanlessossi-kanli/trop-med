"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { api } from "@/lib/api";

interface Patient {
  _id: string;
  given_name: string;
  family_name: string;
  date_of_birth: string;
  gender: string;
}

export default function PatientsPage() {
  const t = useTranslations("patient");
  const tc = useTranslations("common");
  const [patients, setPatients] = useState<Patient[]>([]);
  const [query, setQuery] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token") || "";
    api<{ items: Patient[] }>(`/patients?q=${query}`, { token }).then((d) => setPatients(d.items)).catch(() => {});
  }, [query]);

  return (
    <main style={{ padding: 24 }}>
      <h1>{tc("patients")}</h1>
      <input placeholder={tc("search")} value={query} onChange={(e) => setQuery(e.target.value)} style={{ padding: 8, marginBottom: 16, width: 300 }} />
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>{t("givenName")}</th>
            <th>{t("familyName")}</th>
            <th>{t("dateOfBirth")}</th>
            <th>{t("gender")}</th>
          </tr>
        </thead>
        <tbody>
          {patients.map((p) => (
            <tr key={p._id}>
              <td>{p.given_name}</td>
              <td>{p.family_name}</td>
              <td>{p.date_of_birth}</td>
              <td>{p.gender}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
