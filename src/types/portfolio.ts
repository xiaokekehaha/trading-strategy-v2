// 定义数据类型
export interface PortfolioData {
  frontier_data: {
    volatilities: number[];
    returns: number[];
    sharpes: number[];
  };
  weights_data: {
    weights: number[];
    assets: string[];
  };
  stats: {
    expected_return: number;
    volatility: number;
    sharpe_ratio: number;
  };
  rebalance_suggestions?: RebalanceSuggestion[];
  analysis?: PortfolioAnalysis;
}

export interface RebalanceSuggestion {
  symbol: string;
  name: string;
  action: '买入' | '卖出';
  current_weight: number;
  target_weight: number;
  adjustment: number;
  reason: string;
}

export interface PortfolioAnalysis {
  stats: {
    [key: string]: {
      name: string;
      sector: string;
      industry: string;
      market_cap: number;
      pe_ratio: number;
      dividend_yield: number;
    };
  };
  annual_returns: { [key: string]: number };
  annual_volatility: { [key: string]: number };
  sharpe_ratios: Array<{ symbol: string; sharpe: number }>;
}

// 定义表单数据类型
export interface OptimizationFormData {
  symbols?: string;
  lookback_years?: number;
  target_return: number;
  risk_free_rate: number;
} 