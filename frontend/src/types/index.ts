export interface BacktestParams {
    symbol: string;
    startDate: string;
    endDate: string;
    strategy: {
        name: string;
        params: Record<string, number>;
    };
    initial_capital?: number;
}

export interface StrategyMetrics {
    total_return: number;
    annual_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    win_rate: number;
    total_trades: number;
}

export interface ChartData {
    time: string;
    value: number;
}

interface Trade {
  time: string;
  type: 'buy' | 'sell';
  price: number;
  size: number;
  profit: number | null;
}

export interface PriceData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface BacktestResult {
    metrics: StrategyMetrics;
    equity_curve: ChartData[];
    drawdown: ChartData[];
    trades: Trade[];
    price_data: PriceData[];
}

export interface PortfolioParams {
    symbols: string[];
    startDate: string;
    endDate: string;
    initialCapital: number;
    riskFreeRate?: number;
    targetReturn?: number;
} 