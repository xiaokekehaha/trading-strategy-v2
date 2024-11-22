export interface PortfolioParams {
  symbols: string[];
  startDate: string;
  endDate: string;
  riskFreeRate: number;
  targetReturn: number;
}

export interface PortfolioAsset {
  symbol: string;
  weight: number;
  returns: number;
  risk: number;
}

export interface PortfolioMetrics {
  total_return: number;
  annual_return: number;
  volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  correlation_matrix: Record<string, Record<string, number>>;
}

export interface PortfolioOptimizationResult {
  optimal_weights: Record<string, number>;
  metrics: PortfolioMetrics;
  efficient_frontier: Array<{
    return: number;
    risk: number;
    weights: Record<string, number>;
  }>;
}

export interface PortfolioAnalysisResult {
  assets: PortfolioAsset[];
  metrics: PortfolioMetrics;
  optimization: PortfolioOptimizationResult;
  historical_data: {
    time: string;
    value: number;
    weights: Record<string, number>;
  }[];
}

export interface PortfolioAllocation {
  [symbol: string]: number;
}

export interface PortfolioResult {
  metrics: PortfolioMetrics;
  allocation: PortfolioAllocation;
  returns: Array<{
    date: string;
    value: number;
  }>;
} 