'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import type { BacktestParams, BacktestResult } from '@/types';
import api from '@/lib/api';
import StrategyMetricsComponent from '@/components/StrategyMetrics';
import BacktestChartComponent from '@/components/BacktestChart';
import TradesTableComponent from '@/components/TradesTable';
import StrategyDescriptionComponent from '@/components/StrategyDescription';
import StrategyForm from '@/components/StrategyForm';

export default function AnalysisPage() {
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [selectedStrategy, setSelectedStrategy] = useState('bollinger_bands');

  const { mutate: runBacktest, isPending } = useMutation<
    BacktestResult,
    Error,
    BacktestParams,
    unknown
  >({
    mutationFn: async (params) => {
      const { data } = await api.post<BacktestResult>('/api/backtest/run', params);
      return data;
    },
    onSuccess: (data) => {
      setResult(data);
    },
  });

  const handleStrategyChange = (strategy: string) => {
    setSelectedStrategy(strategy);
  };

  return (
    <div className="container mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">策略分析</h2>
      
      <StrategyDescriptionComponent strategy={selectedStrategy} />
      
      <StrategyForm 
        onSubmit={runBacktest} 
        isLoading={isPending}
        onStrategyChange={handleStrategyChange}
      />
      
      {result && (
        <div className="space-y-8">
          <StrategyMetricsComponent metrics={result.metrics} />
          <BacktestChartComponent result={result} />
          <TradesTableComponent result={result} />
        </div>
      )}
    </div>
  );
} 