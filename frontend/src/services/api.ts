import axios from 'axios';
import type { BacktestResult, StrategyConfig, Strategy, PortfolioResult } from '@/types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL
});

export const getStrategies = async (): Promise<Strategy[]> => {
  const { data } = await api.get('/strategies');
  return data;
};

export const getStrategyParams = async (strategyName: string): Promise<any> => {
  const { data } = await api.get(`/strategies/${strategyName}/params`);
  return data;
};

export const runBacktest = async (params: {
  symbol: string;
  startDate: string;
  endDate: string;
  strategy: StrategyConfig;
  initial_capital?: number;
}): Promise<BacktestResult> => {
  const { data } = await api.post('/backtest/run', {
    symbol: params.symbol,
    startDate: params.startDate,
    endDate: params.endDate,
    strategy: {
      name: params.strategy.name,
      params: params.strategy.params
    },
    initial_capital: params.initial_capital || 100000.0
  });
  return data;
};

export const optimizePortfolio = async (params: {
  symbols: string[];
  startDate: string;
  endDate: string;
  strategies: StrategyConfig[];
}): Promise<PortfolioResult> => {
  const { data } = await api.post('/portfolio/optimize', params);
  return data;
}; 