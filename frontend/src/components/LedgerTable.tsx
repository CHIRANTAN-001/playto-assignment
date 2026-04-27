import { BookOpen, Loader2 } from "lucide-react";
import { fmtINR, fmtDate } from "../lib/format";
import type { LedgerEntry } from "../types";

interface LedgerTableProps {
  entries: LedgerEntry[];
  loading: boolean;
  hasNextPage: boolean;
  isFetchingNextPage: boolean;
  onLoadMore: () => void;
}

export default function LedgerTable({
  entries,
  loading,
  hasNextPage,
  isFetchingNextPage,
  onLoadMore,
}: LedgerTableProps) {
  return (
    <div className="bg-surface border border-border-default rounded-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 px-5 py-4 border-b border-border-default text-[13px] font-semibold text-text-muted">
        <BookOpen size={13} className="text-text-dim" />
        Ledger
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full table-fixed border-collapse">
          <thead>
            <tr>
              <th className="w-[12%] text-left text-[10px] font-semibold text-text-faint uppercase tracking-widest px-5 py-2.5">
                Type
              </th>
              <th className="w-[20%] text-left text-[10px] font-semibold text-text-faint uppercase tracking-widest px-5 py-2.5">
                Amount
              </th>
              <th className="w-[43%] text-left text-[10px] font-semibold text-text-faint uppercase tracking-widest px-5 py-2.5">
                Description
              </th>
              <th className="w-[25%] text-left text-[10px] font-semibold text-text-faint uppercase tracking-widest px-5 py-2.5">
                Date
              </th>
            </tr>
          </thead>
          <tbody>
            {/* Loading */}
            {loading && entries.length === 0 && (
              <tr>
                <td
                  colSpan={4}
                  className="text-center text-text-faint py-10 px-5 border-t border-border-default"
                >
                  <Loader2
                    size={16}
                    className="text-text-dim animate-spin-slow inline-block"
                  />
                </td>
              </tr>
            )}

            {/* Empty */}
            {!loading && entries.length === 0 && (
              <tr>
                <td
                  colSpan={4}
                  className="text-center text-text-faint text-xs py-10 px-5 border-t border-border-default"
                >
                  No ledger entries
                </td>
              </tr>
            )}

            {/* Rows */}
            {entries.map((e) => (
              <tr
                key={e.id}
                className={`hover:bg-border-default/20 transition-colors ${
                  e.entry_type === "credit"
                    ? "bg-success/[0.03]"
                    : "bg-error/[0.03]"
                }`}
              >
                {/* Type badge */}
                <td className="px-5 py-2.5 border-t border-border-default">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-semibold tracking-wide border ${
                      e.entry_type === "credit"
                        ? "bg-success-bg text-success border-success-border"
                        : "bg-error-bg text-error border-error-border"
                    }`}
                  >
                    {e.entry_type}
                  </span>
                </td>

                {/* Amount */}
                <td
                  className={`px-5 py-2.5 border-t border-border-default text-xs font-semibold ${
                    e.entry_type === "credit" ? "text-success" : "text-error"
                  }`}
                >
                  {e.entry_type === "debit" ? "−" : "+"}
                  {fmtINR(e.amount_paise)}
                </td>

                {/* Description — truncated to prevent overflow */}
                <td className="px-5 py-2.5 border-t border-border-default text-xs text-text-subtle truncate max-w-0">
                  <span className="block truncate" title={e.description}>
                    {e.description}
                  </span>
                </td>

                {/* Date */}
                <td className="px-5 py-2.5 border-t border-border-default text-xs text-text-dim whitespace-nowrap">
                  {fmtDate(e.created_at)}
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
