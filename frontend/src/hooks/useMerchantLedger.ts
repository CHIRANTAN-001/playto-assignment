import { useInfiniteQuery } from "@tanstack/react-query";
import client from "../api/client";
import type { ApiResponse, PaginatedResponse, LedgerEntry } from "../types";

export const useMerchantLedger = (merchantId: string | undefined) => {
  return useInfiniteQuery({
    queryKey: ["ledger", merchantId],
    queryFn: async ({ pageParam }) => {
      const params: Record<string, string> = {};
      if (pageParam) params.cursor = pageParam;
      const { data } = await client.get<
        ApiResponse<PaginatedResponse<LedgerEntry>>
      >(`/merchants/${merchantId}/ledger/`, { params });
      return data.data;
    },
    initialPageParam: null as string | null,
    getNextPageParam: (lastPage) =>
      lastPage.has_next ? lastPage.next_cursor : undefined,
    enabled: !!merchantId,
  });
};
