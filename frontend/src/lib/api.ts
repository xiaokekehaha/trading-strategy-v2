import axios from 'axios';
import { MarketData, KLineData } from '@/types/market';
import { BacktestParams, BacktestResult } from '@/types/backtest';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000,
});

export const marketApi = {
  // 获取股票基本信息
  getStockInfo: async (symbol: string): Promise<MarketData> => {
    const { data } = await api.get(`/api/stock/${symbol}/info`);
    return data;
  },

  // 获取K线数据
  getKLineData: async (symbol: string, timeframe: string, start?: string, end?: string) => {
    const { data } = await api.get<KLineData[]>(`/api/stock/${symbol}/kline`, {
      params: { timeframe, start, end }
    });
    return data;
  },

  // 搜索股票
  searchStocks: async (query: string) => {
    const { data } = await api.get('/api/stock/search', {
      params: { query }
    });
    return data;
  },
  
  // 获取自选股列表
  getWatchlist: async () => {
    const { data } = await api.get('/api/watchlist');
    return data;
  },

  // 添加自选股
  addToWatchlist: async (symbol: string) => {
    const { data } = await api.post('/api/watchlist/add', { symbol });
    return data;
  },

  // 删除自选股
  removeFromWatchlist: async (symbol: string) => {
    const { data } = await api.delete(`/api/watchlist/${symbol}`);
    return data;
  }
};

export const backtestApi = {
  // 运行回测
  runBacktest: async (params: BacktestParams): Promise<BacktestResult> => {
    const { data } = await api.post('/api/backtest/run', params);
    return data;
  },

  // 获取回测历史
  getBacktestHistory: async () => {
    const { data } = await api.get('/api/backtest/history');
    return data;
  },

  // 获取策略列表
  getStrategies: async () => {
    const { data } = await api.get('/api/backtest/strategies');
    return data;
  }
}; 