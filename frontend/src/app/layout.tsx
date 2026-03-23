import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Trop-Med",
  description: "Plateforme de médecine tropicale alimentée par l'IA",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
