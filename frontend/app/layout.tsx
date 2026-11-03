import "./globals.css";
import type { Metadata } from "next";
import { Navigation } from "../components/Navigation";
import { Header } from "../components/Header";

export const metadata: Metadata = {
  title: "PULSAR AI V2.0 — Quantitative Crypto Futures Platform",
  description: "Institutional ICT/SMC Crypto Futures Signal and Analysis Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="flex h-screen overflow-hidden bg-background">
        <Navigation />
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <Header />
          <main className="flex-1 overflow-y-auto p-6">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
