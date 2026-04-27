import { useState, useCallback } from "react";
import { BarChart2, Layers } from "lucide-react";
import Navbar from "../components/Navbar";
import BalanceCards from "../components/BalanceCards";
import PayoutForm from "../components/PayoutForm";
import PayoutTable from "../components/PayoutTable";
import LedgerTable from "../components/LedgerTable";
import Toast, { type ToastItem } from "../components/Toast";
import { getMerchantId, getMerchantName } from "../lib/cookies";
import { useMerchantBalance } from "../hooks/useMerchantBalance";
import { useMerchantPayouts } from "../hooks/useMerchantPayouts";
import { useMerchantLedger } from "../hooks/useMerchantLedger";
import { useBankAccounts } from "../hooks/useBankAccounts";
import { useCreatePayout } from "../hooks/useCreatePayout";

interface DashboardPageProps {
  onLogout: () => void;
}

export default function DashboardPage({ onLogout }: DashboardPageProps) {
  const merchantId = getMerchantId();
  const merchantName = getMerchantName() ?? "Merchant";

  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const [activeTab, setActiveTab] = useState<"payouts" | "ledger">("payouts");

  // ── Data Hooks ────────────────────────────────────────────────
  const balanceQuery = useMerchantBalance(merchantId);
  const payoutsQuery = useMerchantPayouts(merchantId);
  const ledgerQuery = useMerchantLedger(merchantId);
  const bankAccountsQuery = useBankAccounts(merchantId);
  const createPayoutMutation = useCreatePayout(merchantId);

  // ── Flatten paginated data ────────────────────────────────────
  const payouts = payoutsQuery.data?.pages.flatMap((p) => p.results) ?? [];
  const ledgerEntries =
    ledgerQuery.data?.pages.flatMap((p) => p.results) ?? [];

  // ── Toast helper ──────────────────────────────────────────────
  const addToast = useCallback(
    (msg: string, type: "success" | "error" = "success") => {
      const id = Date.now();
      setToasts((t) => [...t, { id, msg, type }]);
      setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 3500);
    },
    []
  );

  // ── Payout submit ─────────────────────────────────────────────
  const handlePayoutSubmit = (
    amount_paise: number,
    bank_account_id: string
  ) => {
    createPayoutMutation.mutate(
      { amount_paise, bank_account_id },
      {
        onSuccess: () => addToast("Payout submitted successfully", "success"),
        onError: (error: any) => {
          const msg =
            error?.response?.data?.message || "Failed to create payout";
          addToast(msg, "error");
        },
      }
    );
  };

  return (
    <div className="flex flex-col min-h-screen bg-base">
      <Navbar merchantName={merchantName} onLogout={onLogout} />

      <div className="flex-1 p-6 max-w-[1100px] w-full mx-auto">
        {/* ── Overview ───────────────────────────────────────────── */}
        <div className="flex items-center gap-1.5 text-[11px] font-semibold text-text-dim uppercase tracking-widest mb-3">
          <BarChart2 size={11} className="text-text-dim" />
          Overview
        </div>
        <BalanceCards
          balance={balanceQuery.data?.balance}
          loading={balanceQuery.isLoading}
        />

        {/* ── Operations ─────────────────────────────────────────── */}
        <div className="flex items-center gap-1.5 text-[11px] font-semibold text-text-dim uppercase tracking-widest mb-3">
          <Layers size={11} className="text-text-dim" />
          Operations
        </div>

        <div className="grid grid-cols-[300px_1fr] gap-4">
          {/* Left: Payout form */}
          <PayoutForm
            bankAccounts={bankAccountsQuery.data ?? []}
            bankAccountsLoading={bankAccountsQuery.isLoading}
            submitting={createPayoutMutation.isPending}
            onSubmit={handlePayoutSubmit}
          />

          {/* Right: Tables */}
          <div>
            {/* Tabs */}
            <div className="flex gap-px bg-border-default rounded-lg p-0.5 w-fit mb-3">
              {(["payouts", "ledger"] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-1.5 rounded-md text-xs font-medium border-none cursor-pointer transition-colors ${
                    activeTab === tab
                      ? "bg-tab-active text-text-secondary"
                      : "bg-transparent text-text-dim hover:text-text-muted"
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            {/* Active table */}
            {activeTab === "payouts" ? (
              <PayoutTable
                payouts={payouts}
                loading={payoutsQuery.isLoading}
                hasNextPage={!!payoutsQuery.hasNextPage}
                isFetchingNextPage={payoutsQuery.isFetchingNextPage}
                onLoadMore={() => payoutsQuery.fetchNextPage()}
              />
            ) : (
              <LedgerTable
                entries={ledgerEntries}
                loading={ledgerQuery.isLoading}
                hasNextPage={!!ledgerQuery.hasNextPage}
                isFetchingNextPage={ledgerQuery.isFetchingNextPage}
                onLoadMore={() => ledgerQuery.fetchNextPage()}
              />
            )}
          </div>
        </div>
      </div>

      <Toast toasts={toasts} />
    </div>
  );
}
