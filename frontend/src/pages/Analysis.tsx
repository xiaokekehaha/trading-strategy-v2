import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import type { BacktestParams, BacktestResult } from '@/types';
import api from '@/utils/api';
import StrategyMetrics from '@/components/StrategyMetrics';

const Analysis: React.FC = () => {
  const [result, setResult] = useState<BacktestResult | null>(null);

  const { mutate: runBacktest, isLoading } = useMutation<
    BacktestResult,
    Error,
    BacktestParams
  >(
    async (params) => {
      const { data } = await api.post<BacktestResult>('/backtest/run', params);
      return data;
    },
    {
      onSuccess: (data) => {
        setResult(data);
      },
    }
  );

  return (
    <div>
      {result && <StrategyMetrics metrics={result.metrics} />}
    </div>
  );
};

export default Analysis; 