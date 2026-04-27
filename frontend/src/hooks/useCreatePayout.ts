import { useMutation, useQueryClient } from "@tanstack/react-query";
import client from "../api/client";
import type { ApiResponse, Payout } from "../types";

interface CreatePayoutParams {
  amount_paise: number;
  bank_account_id: string;
}

export const useCreatePayout = (merchantId: string | undefined) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ amount_paise, bank_account_id }: CreatePayoutParams) => {
      const idempotencyKey = crypto.randomUUID();
      const { data } = await client.post<ApiResponse<Payout>>(
        "/payouts/",
        { amount_paise, bank_account_id },
        { headers: { "Idempotency-Key": idempotencyKey } }
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["balance", merchantId] });
      queryClient.invalidateQueries({ queryKey: ["payouts", merchantId] });
      queryClient.invalidateQueries({ queryKey: ["ledger", merchantId] });
    },
  });
};
