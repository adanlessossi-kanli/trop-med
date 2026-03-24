import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Trop-Med",
  description: "Plateforme de médecine tropicale alimentée par l'IA",
  icons: { icon: "data:," },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html>
      <body>{children}</body>
    </html>
  );
}
