'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import type { BacktestResult } from '@/types';
import MetricsTrendChart from '@/components/MetricsTrendChart';
import StrategyComparison from '@/components/StrategyComparison';
import RiskAnalysis from '@/components/RiskAnalysis';
import StrategyOptimization from '@/components/StrategyOptimization';

export default function MetricsPage() {
  const [selectedResult, setSelectedResult] = useState<BacktestResult | null>(null);
  
  const { data: results } = useQuery({
    queryKey: ['backtest-results'],
    queryFn: async () => {
      const { data } = await api.get<BacktestResult[]>('/api/backtest/results');
      return data;
    }
  });

  useEffect(() => {
    if (results?.length) {
      setSelectedResult(results[0]);
    }
  }, [results]);

  if (!selectedResult) return null;

  return (
    <div className="container mx-auto p-4 space-y-8">
      <h2 className="text-2xl font-bold mb-4">策略分析报告</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MetricsTrendChart
          data={{
            labels: selectedResult.equity_curve.map(p => p.time),
            datasets: [
              {
                label: '收益率趋势',
                data: selectedResult.equity_curve.map(p => ((p.value - selectedResult.equity_curve[0].value) / selectedResult.equity_curve[0].value) * 100),
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
              }
            ]
          }}
          title="收益率趋势分析"
        />
        
        {results && (
          <StrategyComparison
            strategies={results.map(r => ({
              name: r.strategy.name,
              metrics: r.metrics
            }))}
          />
        )}
      </div>
      
      <RiskAnalysis result={selectedResult} />
      
      <StrategyOptimization result={selectedResult} />
    </div>
  );
} 