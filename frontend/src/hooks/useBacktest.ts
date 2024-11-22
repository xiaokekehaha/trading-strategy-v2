import { useMutation } from '@tanstack/react-query';
import { runBacktest as runBacktestApi } from '@/services/api';
import type { BacktestParams, BacktestResult } from '@/types/backtest';

export const useBacktest = () => {
  const { mutate, isLoading, error, data } = useMutation<
    BacktestResult,
    Error,
    BacktestParams
  >(runBacktestApi);

  return {
    runBacktest: mutate,
    isLoading,
    error,
    result: data
  };
}; 