import type { PayoutStatus } from "../types";

const cfg: Record<PayoutStatus, { dot: string; bg: string; text: string; border: string }> = {
  pending:    { dot: "bg-warning",  bg: "bg-warning-bg",  text: "text-warning",  border: "border-warning-border" },
  processing: { dot: "bg-info",     bg: "bg-info-bg",     text: "text-info",     border: "border-info-border" },
  completed:  { dot: "bg-success",  bg: "bg-success-bg",  text: "text-success",  border: "border-success-border" },
  failed:     { dot: "bg-error",    bg: "bg-error-bg",    text: "text-error",    border: "border-error-border" },
};

export default function StatusBadge({ status }: { status: PayoutStatus }) {
  const s = cfg[status] ?? cfg.pending;
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-semibold tracking-wide border ${s.bg} ${s.text} ${s.border}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />
      {status}
    </span>
  );
}
