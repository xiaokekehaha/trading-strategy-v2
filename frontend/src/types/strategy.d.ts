export interface BaseStrategyParams {
  window?: number;
  num_std?: number;
  fast_period?: number;
  slow_period?: number;
  signal_period?: number;
  lookback_period?: number;
  n_days?: number;
}

export interface StrategyConfig {
  name: string;
  params: BaseStrategyParams;
}

export interface StrategyMetrics {
  total_return: number;
  annual_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  volatility: number;
}

export interface StrategyResult extends StrategyMetrics {
  returns: Array<{
    time: string;
    value: number;
  }>;
  drawdown: Array<{
    time: string;
    value: number;
  }>;
} 