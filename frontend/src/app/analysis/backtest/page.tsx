'use client';

import React from 'react';
import { useMutation } from '@tanstack/react-query';
import type { BacktestParams, BacktestResult } from '@/types/backtest';
import { backtestApi } from '@/lib/api';
import { STRATEGY_CONFIGS } from '@/lib/constants';
import StrategyForm from '@/components/StrategyForm';
import StrategyDescription from '@/components/StrategyDescription';
import BacktestChart from '@/components/BacktestChart';
import MetricsDetail from '@/components/MetricsDetail';
import TradesTable from '@/components/TradesTable';
import DeepLearningMetrics from '@/components/DeepLearningMetrics';

export default function BacktestPage() {
  // 设置默认日期范围：结束日期为昨天，开始日期为90天前
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);
  const defaultEndDate = yesterday.toISOString().split('T')[0];

  const defaultStartDate = new Date(yesterday);
  defaultStartDate.setDate(yesterday.getDate() - 90);

  // 状态管理
  const [formData, setFormData] = React.useState<BacktestParams>({
    symbol: 'AAPL',
    startDate: defaultStartDate.toISOString().split('T')[0],
    endDate: defaultEndDate,
    strategy: {
      name: 'bollinger_bands',
      params: {
        window: 20,
        num_std: 2.0
      }
    }
  });

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
    setResult(null);
    
    // 更新策略参数
    const defaultParams = STRATEGY_CONFIGS[strategy].params;
    const params: Record<string, number> = {};
    Object.entries(defaultParams).forEach(([key, config]) => {
      params[key] = config.default;
    });

    setFormData(prev => ({
      ...prev,
      strategy: {
        name: strategy,
        params
      }
    }));
  };

  const handleSubmit = (params: BacktestParams) => {
    setFormData(params);
    runBacktest(params);
  };

  const isDeepLearning = ['mlp', 'lstm_mlp', 'cnn_mlp'].includes(selectedStrategy);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-white">策略回测</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 左侧表单区域 */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-[#1E293B] rounded-lg p-6 shadow-lg border border-gray-700">
              <StrategyDescription strategy={selectedStrategy} />
            </div>
            <div className="bg-[#1E293B] rounded-lg p-6 shadow-lg border border-gray-700">
              <StrategyForm
                defaultValues={formData}
                onSubmit={handleSubmit}
                isLoading={isPending}
                onStrategyChange={handleStrategyChange}
              />
            </div>
          </div>

          {/* 右侧结果区域 */}
          <div className="lg:col-span-2">
            <div className="bg-[#1E293B] rounded-lg p-6 shadow-lg border border-gray-700">
              {isPending ? (
                <div className="flex items-center justify-center h-96">
                  <div className="text-lg text-gray-300">正在进行回测分析...</div>
                </div>
              ) : result ? (
                <div className="space-y-8">
                  <BacktestChart
                    returns={result.equity_curve}
                    drawdown={result.drawdown_curve}
                    positions={result.positions}
                    dates={result.dates}
                    trades={result.trades}
                    stockData={result.stockData}
                  />
                  <MetricsDetail metrics={result.metrics} />
                  {isDeepLearning && result.training_history && (
                    <DeepLearningMetrics trainingHistory={result.training_history} />
                  )}
                  <TradesTable 
                    trades={result.trades} 
                    metrics={result.metrics} 
                  />
                </div>
              ) : (
                <div className="flex items-center justify-center h-96 text-gray-400">
                  请设置参数开始回测
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 