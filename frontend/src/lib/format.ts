export const fmtINR = (paise: number): string =>
  "₹" +
  (paise / 100).toLocaleString("en-IN", { maximumFractionDigits: 0 });

export const fmtINRFromINR = (inr: number): string =>
  "₹" + Number(inr).toLocaleString("en-IN", { maximumFractionDigits: 0 });

export const fmtDate = (iso: string): string =>
  new Date(iso).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });

export const shortId = (id: string): string => id.slice(0, 8);
