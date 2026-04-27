import { useQuery } from "@tanstack/react-query";
import client from "../api/client";
import type { ApiResponse, MerchantBalance } from "../types";

export const useMerchantBalance = (merchantId: string | undefined) => {
  return useQuery({
    queryKey: ["balance", merchantId],
    queryFn: async () => {
      const { data } = await client.get<ApiResponse<MerchantBalance>>(
        `/merchants/${merchantId}/balance/`
      );
      return data.data;
    },
    enabled: !!merchantId,
    refetchInterval: 10_000,
  });
};
