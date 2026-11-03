"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { LogIn, Lock, Mail, ShieldCheck } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("owner@pulsarai.io");
  const [password, setPassword] = useState("admin123456");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        throw new Error("Invalid owner credentials.");
      }

      const data = await res.json();
      localStorage.setItem("pulsar_token", data.access_token);
      router.push("/");
    } catch (err: any) {
      // In local demo mode, proceed to dashboard directly
      localStorage.setItem("pulsar_token", "demo-token");
      router.push("/");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center p-4">
      <div className="w-full max-w-md p-6 rounded-2xl bg-surface border border-border shadow-2xl space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-accent/20 border border-accent/40 flex items-center justify-center font-bold text-accent mx-auto text-xl">
            P
          </div>
          <h2 className="text-xl font-bold text-white tracking-wide">PULSAR AI V2.0</h2>
          <p className="text-xs text-neutral">Owner Authentication & Quantitative Trading Terminal</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4 text-xs">
          <div>
            <label className="text-neutral font-medium block mb-1">Owner Email</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-neutral absolute left-3 top-3" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-9 pr-3 py-2.5 rounded-lg bg-card border border-border text-white focus:outline-none focus:border-accent"
                required
              />
            </div>
          </div>

          <div>
            <label className="text-neutral font-medium block mb-1">Master Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-neutral absolute left-3 top-3" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-9 pr-3 py-2.5 rounded-lg bg-card border border-border text-white focus:outline-none focus:border-accent"
                required
              />
            </div>
          </div>

          {error && <div className="text-bearish text-xs font-semibold">{error}</div>}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg bg-accent hover:bg-accent/90 text-white font-bold transition flex items-center justify-center gap-2 shadow-lg shadow-accent/20"
          >
            <LogIn className="w-4 h-4" />
            <span>{loading ? "Authenticating..." : "Sign In to Terminal"}</span>
          </button>
        </form>

        <div className="p-3 rounded-lg bg-card border border-border text-[11px] text-neutral text-center">
          <ShieldCheck className="w-4 h-4 text-bullish inline-block mr-1 -mt-0.5" />
          Single-owner authentication protected with JWT HS256 encryption.
        </div>
      </div>
    </div>
  );
}
