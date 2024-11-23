'use client';

import React from 'react';
import { useMutation } from '@tanstack/react-query';
import type { BacktestParams, BacktestResult } from '@/types';
import { backtestApi } from '@/lib/api';
import StrategyForm from '@/components/StrategyForm';
import StrategyDescription from '@/components/StrategyDescription';
import BacktestChart from '@/components/BacktestChart';
import MetricsDetail from '@/components/MetricsDetail';
import TradesTable from '@/components/TradesTable';
import DeepLearningMetrics from '@/components/DeepLearningMetrics';

export default function AnalysisPage() {
  const [selectedStrategy, setSelectedStrategy] = React.useState('bollinger_bands');
  const [result, setResult] = React.useState<BacktestResult | null>(null);

  const { mutate: runBacktest, isPending } = useMutation({
    mutationFn: (params: BacktestParams) => backtestApi.runBacktest(params),
    onSuccess: (data) => {
      setResult(data);
    },
    onError: (error) => {
      console.error('回测失败:', error);
      alert('回测失败，请检查参数后重试');
    }
  });

  const handleStrategyChange = (strategy: string) => {
    setSelectedStrategy(strategy);
    setResult(null);  // 清除之前的结果
  };

  const handleSubmit = (params: BacktestParams) => {
    runBacktest(params);
  };

  const isDeepLearning = ['mlp', 'lstm_mlp', 'cnn_mlp'].includes(selectedStrategy);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">策略分析</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* 左侧表单区域 */}
        <div className="lg:col-span-1">
          <StrategyDescription strategy={selectedStrategy} />
          <StrategyForm
            onSubmit={handleSubmit}
            isLoading={isPending}
            onStrategyChange={handleStrategyChange}
          />
        </div>

        {/* 右侧结果区域 */}
        <div className="lg:col-span-2">
          {isPending ? (
            <div className="flex items-center justify-center h-96">
              <div className="text-lg">正在进行回测分析...</div>
            </div>
          ) : result ? (
            <div className="space-y-8">
              <BacktestChart
                returns={result.equity_curve}
                drawdown={result.drawdown_curve}
                positions={result.positions}
                dates={result.dates}
              />
              <MetricsDetail metrics={result.metrics} />
              {isDeepLearning && result.training_history && (
                <DeepLearningMetrics trainingHistory={result.training_history} />
              )}
              <TradesTable trades={result.trades} />
            </div>
          ) : (
            <div className="flex items-center justify-center h-96 text-gray-500">
              请设置参数开始回测
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 