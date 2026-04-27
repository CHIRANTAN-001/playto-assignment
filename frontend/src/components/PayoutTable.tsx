import { Activity, Loader2 } from "lucide-react";
import StatusBadge from "./StatusBadge";
import { fmtINR, fmtDate, shortId } from "../lib/format";
import type { Payout } from "../types";

interface PayoutTableProps {
  payouts: Payout[];
  loading: boolean;
  hasNextPage: boolean;
  isFetchingNextPage: boolean;
  onLoadMore: () => void;
}

export default function PayoutTable({
  payouts,
  loading,
  hasNextPage,
  isFetchingNextPage,
  onLoadMore,
}: PayoutTableProps) {
  return (
    <div className="bg-surface border border-border-default rounded-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-border-default">
        <div className="flex items-center gap-2 text-[13px] font-semibold text-text-muted">
          <Activity size={13} className="text-text-dim" />
          Payout history
        </div>
        <span className="text-[10px] text-text-faint">live · 5s</span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full table-fixed border-collapse">
          <thead>
            <tr>
              <th className="w-[15%] text-left text-[10px] font-semibold text-text-faint uppercase tracking-widest px-5 py-2.5">
                ID
              </th>
              <th className="w-[20%] text-left text-[10px] font-semibold text-text-faint uppercase tracking-widest px-5 py-2.5">
                Amount
              </th>
              <th className="w-[25%] text-left text-[10px] font-semibold text-text-faint uppercase tracking-widest px-5 py-2.5">
                Bank
              </th>
              <th className="w-[18%] text-left text-[10px] font-semibold text-text-faint uppercase tracking-widest px-5 py-2.5">
                Status
              </th>
              <th className="w-[22%] text-left text-[10px] font-semibold text-text-faint uppercase tracking-widest px-5 py-2.5">
                Created
              </th>
            </tr>
          </thead>
          <tbody>
            {/* Loading skeleton */}
            {loading && payouts.length === 0 && (
              <tr>
                <td
                  colSpan={5}
                  className="text-center text-text-faint py-10 px-5 border-t border-border-default"
                >
                  <Loader2
                    size={16}
                    className="text-text-dim animate-spin-slow inline-block"
                  />
                </td>
              </tr>
            )}

            {/* Empty state */}
            {!loading && payouts.length === 0 && (
              <tr>
                <td
                  colSpan={5}
                  className="text-center text-text-faint text-xs py-10 px-5 border-t border-border-default"
                >
                  No payouts yet
                </td>
              </tr>
            )}

            {/* Data rows */}
            {payouts.map((p) => (
              <tr key={p.id} className="hover:bg-border-default/20 transition-colors">
                <td className="px-5 py-2.5 border-t border-border-default font-mono text-[11px] text-text-subtle truncate">
                  {shortId(p.id)}
                </td>
                <td className="px-5 py-2.5 border-t border-border-default text-xs font-semibold text-text-secondary">
                  {fmtINR(p.amount_paise)}
                </td>
                <td className="px-5 py-2.5 border-t border-border-default font-mono text-[11px] text-text-subtle truncate">
                  {p.bank_account.masked_account_number}
                </td>
                <td className="px-5 py-2.5 border-t border-border-default">
                  <StatusBadge status={p.status} />
                </td>
                <td className="px-5 py-2.5 border-t border-border-default text-xs text-text-dim">
                  {fmtDate(p.created_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Load More */}
      {hasNextPage && (
        <div className="px-5 py-3 border-t border-border-default">
          <button
            onClick={onLoadMore}
            disabled={isFetchingNextPage}
            className="flex items-center gap-1.5 px-4 py-1.5 text-xs text-text-dim border border-border-subtle rounded-md hover:border-text-dim transition-colors cursor-pointer disabled:cursor-not-allowed"
          >
            {isFetchingNextPage && (
              <Loader2 size={12} className="animate-spin-slow" />
            )}
            {isFetchingNextPage ? "Loading…" : "Load more"}
          </button>
        </div>
      )}
    </div>
  );
}
