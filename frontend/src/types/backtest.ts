export interface BacktestParams {
  symbol: string;
  startDate: string;
  endDate: string;
  strategy: {
    name: string;
    params: Record<string, number>;
  };
}

export interface TradeRecord {
  date: string;
  type: 'buy' | 'sell';
  price: number;
  shares: number;
  profit: number;
}

export interface BacktestMetrics {
  total_return: number;
  annual_return: number;
  volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  trades_count: number;
  profit_factor: number;
  recovery_factor: number;
  risk_return_ratio: number;
}

export interface StockData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface BacktestResult {
  trades: TradeRecord[];
  metrics: BacktestMetrics;
  equity_curve: number[];
  drawdown_curve: number[];
  positions: number[];
  dates: string[];
  stockData: StockData[];
  training_history?: {
    loss: number[];
    accuracy: number[];
    val_loss?: number[];
    val_accuracy?: number[];
  };
}

export interface StrategyMetrics {
  total_return: number;
  annual_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  total_trades: number;
  volatility: number;
} 