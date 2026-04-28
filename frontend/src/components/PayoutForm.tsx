import { useState } from "react";
import { Send, ArrowUpRight, Loader2, ChevronDown } from "lucide-react";
import type { BankAccount } from "../types";

interface PayoutFormProps {
  bankAccounts: BankAccount[];
  bankAccountsLoading: boolean;
  submitting: boolean;
  onSubmit: (amount_paise: number, bank_account_id: string) => void;
}

export default function PayoutForm({
  bankAccounts,
  bankAccountsLoading,
  submitting,
  onSubmit,
}: PayoutFormProps) {
  const [amount, setAmount] = useState("");
  const [bankId, setBankId] = useState("");

  const handleSubmit = () => {
    const val = Number(amount);
    if (!amount || isNaN(val) || val < 1 || !bankId) return;
    onSubmit(val * 100, bankId);
    setAmount("");
  };

  const disabled = submitting || !amount || Number(amount) < 1 || !bankId;

  return (
    <div className="bg-surface border border-border-default rounded-xl p-5">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <Send size={14} className="text-accent" />
        <span className="text-[13px] font-semibold text-text-muted">
          Request payout
        </span>
      </div>

      {/* Amount */}
      <div className="mb-3.5">
        <label className="block text-[11px] font-semibold text-text-dim uppercase tracking-widest mb-2">
          Amount (₹)
        </label>
        <input
          type="number"
          min="1"
          placeholder="0"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          className="w-full bg-input border border-border-subtle text-text-secondary rounded-lg px-3 py-2.5 text-sm outline-none focus:border-accent transition-colors"
        />
      </div>

      {/* Bank Account */}
      <div className="mb-4.5">
        <label className="block text-[11px] font-semibold text-text-dim uppercase tracking-widest mb-2">
          Bank account
        </label>
        <div className="relative">
          <select
            value={bankId}
            onChange={(e) => setBankId(e.target.value)}
            disabled={bankAccountsLoading || bankAccounts.length === 0}
            className="w-full bg-input border border-border-subtle text-text-secondary rounded-lg pl-3 pr-9 py-2.5 text-[13px] outline-none appearance-none cursor-pointer focus:border-accent transition-colors"
          >
            {bankAccountsLoading && <option value="">Loading accounts…</option>}
            {!bankAccountsLoading && bankAccounts.length === 0 && (
              <option value="">No accounts found</option>
            )}
            {!bankAccountsLoading && bankAccounts.length > 0 && (
              <option value="" disabled>
                Select a bank account
              </option>
            )}
            {bankAccounts.map((b) => (
              <option key={b.id} value={b.id}>
                Account — {b.masked_account_number}
              </option>
            ))}
          </select>
          <ChevronDown
            size={13}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-text-dim pointer-events-none"
          />
        </div>
      </div>

      {/* Submit */}
      <button
        onClick={handleSubmit}
        disabled={disabled}
        className={`w-full flex items-center justify-center gap-2 bg-accent text-white border-none rounded-lg py-2.5 text-[13px] font-semibold transition-opacity cursor-pointer ${
          disabled ? "opacity-50 cursor-not-allowed" : "opacity-100 hover:bg-accent-hover"
        }`}
      >
        {submitting ? (
          <Loader2 size={14} className="animate-spin-slow" />
        ) : (
          <ArrowUpRight size={14} />
        )}
        {submitting ? "Submitting…" : "Submit payout"}
      </button>
    </div>
  );
}
