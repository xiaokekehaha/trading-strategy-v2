import { useQuery } from '@tanstack/react-query';
import { marketApi } from '@/lib/api';
import { MarketData, KLineData, Timeframe } from '@/types/market';

export const useMarketData = (symbol: string) => {
  // 获取股票基本信息
  const { 
    data: quote,
    isLoading: isLoadingQuote,
    error: quoteError
  } = useQuery<MarketData>({
    queryKey: ['stock', symbol],
    queryFn: () => marketApi.getStockInfo(symbol),
    enabled: !!symbol,
    refetchInterval: 60000, // 每分钟刷新一次数据
  });

  // 获取K线数据
  const getKLineData = async (timeframe: Timeframe, start?: string, end?: string) => {
    return marketApi.getKLineData(symbol, timeframe, start, end);
  };

  // 搜索股票
  const searchStocks = async (query: string) => {
    return marketApi.searchStocks(query);
  };

  return {
    quote,
    isLoadingQuote,
    quoteError,
    getKLineData,
    searchStocks
  };
}; 