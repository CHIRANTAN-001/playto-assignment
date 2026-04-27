import { CheckCircle, AlertCircle } from "lucide-react";

export interface ToastItem {
  id: number;
  msg: string;
  type: "success" | "error";
}

export default function Toast({ toasts }: { toasts: ToastItem[] }) {
  return (
    <div className="fixed bottom-6 right-6 z-[999] w-full max-w-sm">
      
      {/* Container with height limit */}
      <div className="flex flex-col gap-2 max-h-80 overflow-y-auto pr-1">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`animate-fade-up flex items-start gap-2.5 w-full rounded-lg px-4 py-3 text-[13px] bg-tab-active border ${
              t.type === "success"
                ? "border-success-border"
                : "border-error-border"
            }`}
          >
            {t.type === "success" ? (
              <CheckCircle size={15} className="shrink-0 mt-[2px]" />
            ) : (
              <AlertCircle size={15} className="shrink-0 mt-[2px]" />
            )}

            <p className="break-words leading-snug">{t.msg}</p>
          </div>
        ))}
      </div>
    </div>
  );
}