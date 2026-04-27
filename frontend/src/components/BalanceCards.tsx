import { TrendingUp, Clock } from "lucide-react";
import { fmtINRFromINR } from "../lib/format";
import type { BalanceInfo } from "../types";

interface BalanceCardsProps {
  balance: BalanceInfo | undefined;
  loading: boolean;
}

export default function BalanceCards({ balance, loading }: BalanceCardsProps) {
  const cards = [
    {
      label: "Available balance",
      icon: <TrendingUp size={12} className="text-success" />,
      value: balance?.available_inr,
      valueColor: "text-success",
      sub: "Ready for payout",
    },
    {
      label: "Held balance",
      icon: <Clock size={12} className="text-warning" />,
      value: balance?.held_inr,
      valueColor: "text-warning",
      sub: "Pending release",
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 mb-6">
      {cards.map((c, i) => (
        <div
          key={i}
          className="bg-surface border border-border-default rounded-xl p-5"
        >
          <div className="flex items-center gap-1.5 text-[11px] text-text-dim mb-2.5">
            {c.icon} {c.label}
          </div>

          {loading ? (
            <div className="w-36 h-7 bg-border-subtle rounded animate-shimmer" />
          ) : (
            <div className={`text-[28px] font-bold tracking-tight mb-1.5 ${c.valueColor}`}>
              {fmtINRFromINR(c.value ?? 0)}
            </div>
          )}

          <div className="text-[11px] text-text-faint">{c.sub}</div>
        </div>
      ))}
    </div>
  );
}
