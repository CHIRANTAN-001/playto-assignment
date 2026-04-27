import { useInfiniteQuery } from "@tanstack/react-query";
import client from "../api/client";
import type { ApiResponse, PaginatedResponse, Payout } from "../types";

export const useMerchantPayouts = (merchantId: string | undefined) => {
  return useInfiniteQuery({
    queryKey: ["payouts", merchantId],
    queryFn: async ({ pageParam }) => {
      const params: Record<string, string> = {};
      if (pageParam) params.cursor = pageParam;
      const { data } = await client.get<
        ApiResponse<PaginatedResponse<Payout>>
      >(`/merchants/${merchantId}/payouts/`, { params });
      return data.data;
    },
    initialPageParam: null as string | null,
    getNextPageParam: (lastPage) =>
      lastPage.has_next ? lastPage.next_cursor : undefined,
    enabled: !!merchantId,
    refetchInterval: 5_000,
  });
};
