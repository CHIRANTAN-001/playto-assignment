import { useQuery } from "@tanstack/react-query";
import client from "../api/client";
import type { ApiResponse, BankAccount } from "../types";

export const useBankAccounts = (merchantId: string | undefined) => {
  return useQuery({
    queryKey: ["bankAccounts", merchantId],
    queryFn: async () => {
      const { data } = await client.get<ApiResponse<BankAccount[]>>(
        `/merchants/${merchantId}/bank-accounts/`
      );
      return data.data;
    },
    enabled: !!merchantId,
  });
};
