// ── API Response Types matching Django backend ──

export interface Merchant {
  id: string;
  name: string;
  email: string;
}

export interface BankAccount {
  id: string;
  masked_account_number: string;
}

export interface BalanceInfo {
  available_paise: number;
  available_inr: number;
  held_paise: number;
  held_inr: number;
  total_paise: number;
  total_inr: number;
}

export interface MerchantBalance {
  merchant_id: string;
  merchant_name: string;
  balance: BalanceInfo;
}

export type PayoutStatus = "pending" | "processing" | "completed" | "failed";

export interface Payout {
  id: string;
  merchant: Merchant;
  amount_paise: number;
  bank_account: BankAccount;
  status: PayoutStatus;
  created_at: string;
  updated_at: string;
}

export interface LedgerEntry {
  id: string;
  entry_type: "credit" | "debit";
  amount_paise: number;
  merchant: Merchant;
  payout_id: string | null;
  description: string;
  created_at: string;
}

export interface ApiResponse<T> {
  data: T;
  message: string;
}

export interface PaginatedResponse<T> {
  results: T[];
  next_cursor: string | null;
  has_next: boolean;
}
