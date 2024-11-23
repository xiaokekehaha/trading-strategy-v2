export interface MarketData {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  open: number;
  high: number;
  low: number;
  close: number;
  avgPrice: number;
  weekHigh52: number;
  weekLow52: number;
  peRatio: number;
  dividendYield: number;
  shortRatio: number;
  floatShares: number;
  lastUpdate: string;
}

export interface KLineData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface MarketDataResponse {
  data: MarketData;
  timestamp: number;
}

export interface MarketDataSubscription {
  symbol: string;
  callback: (data: MarketData) => void;
}

export const TIMEFRAMES = [
  { id: '1D', name: '1天', yf_interval: '1d' },
  { id: '1W', name: '1周', yf_interval: '1wk' },
  { id: '1M', name: '1月', yf_interval: '1mo' },
  { id: '3M', name: '3月', yf_interval: '3mo' },
  { id: '1Y', name: '1年', yf_interval: '1d' },
  { id: 'ALL', name: '全部', yf_interval: '1d' }
] as const;

export type Timeframe = typeof TIMEFRAMES[number]['id'];

// yfinance支持的时间间隔映射
export const YF_INTERVALS: Record<string, string> = {
  '1D': '1d',
  '1W': '1wk',
  '1M': '1mo',
  '3M': '3mo',
  '6M': '1d',  // 使用日线数据
  '1Y': '1d',
  '5Y': '1d',
  'ALL': '1d'
}; 