import { useState } from "react";
import { Zap, ArrowRight, Loader2 } from "lucide-react";
import client from "../api/client";
import { setMerchantCookie } from "../lib/cookies";
import type { ApiResponse, Merchant } from "../types";

interface LoginPageProps {
  onLogin: () => void;
}

export default function LoginPage({ onLogin }: LoginPageProps) {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const handleLogin = async () => {
    if (!email.includes("@")) {
      setErr("Enter a valid email");
      return;
    }
    setLoading(true);
    setErr("");

    try {
      const { data } = await client.post<ApiResponse<Merchant>>(
        "/merchants/login/",
        { email }
      );
      setMerchantCookie(data.data.id, data.data.name);
      onLogin();
    } catch (error: any) {
      const msg = error?.response?.data?.message || "Merchant not found";
      setErr(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-base flex items-center justify-center relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] rounded-full bg-[radial-gradient(ellipse,rgba(99,102,241,0.13)_0%,transparent_70%)] pointer-events-none" />

      {/* Card */}
      <div className="relative z-10 bg-surface border border-border-strong rounded-2xl px-9 py-10 w-[380px]">
        {/* Logo */}
        <div className="flex items-center gap-2.5 mb-8">
          <div className="w-8 h-8 bg-accent rounded-lg flex items-center justify-center">
            <Zap size={16} className="text-white" />
          </div>
          <span className="text-lg font-bold text-text-primary tracking-tight">
            Playto Pay
          </span>
        </div>

        {/* Heading */}
        <h1 className="text-2xl font-bold text-text-primary mb-1.5 tracking-tight">
          Welcome back
        </h1>
        <p className="text-[13px] text-text-subtle mb-7">
          Sign in to your merchant dashboard
        </p>

        {/* Email label */}
        <label className="block text-[11px] font-semibold text-text-subtle uppercase tracking-widest mb-2">
          Email address
        </label>

        {/* Email input */}
        <input
          type="email"
          placeholder="merchant@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleLogin()}
          className={`w-full bg-input border border-border-strong text-text-secondary rounded-lg px-3.5 py-2.5 text-sm outline-none focus:border-accent transition-colors ${
            err ? "mb-2" : "mb-5"
          }`}
        />

        {/* Error */}
        {err && (
          <p className="text-xs text-error mb-3.5">{err}</p>
        )}

        {/* Button */}
        <button
          onClick={handleLogin}
          disabled={loading}
          className={`w-full flex items-center justify-center gap-2 rounded-lg py-3 text-sm font-semibold text-white border-none cursor-pointer transition-all ${
            loading
              ? "bg-accent-hover opacity-80 cursor-not-allowed"
              : "bg-accent hover:bg-accent-hover"
          }`}
        >
          {loading ? (
            <Loader2 size={14} className="animate-spin-slow" />
          ) : (
            <ArrowRight size={14} />
          )}
          {loading ? "Signing in…" : "Sign in"}
        </button>

        {/* Hint */}
        <p className="mt-4 text-[11px] text-text-faint text-center">
          Use your seeded merchant email to login
        </p>
      </div>
    </div>
  );
}
