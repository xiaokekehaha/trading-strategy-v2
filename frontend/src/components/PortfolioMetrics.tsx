'use client';

import React from 'react';
import type { PortfolioMetrics } from '@/types/portfolio';

interface Props {
  metrics: PortfolioMetrics;
}

const MetricCard = ({ label, value, format }: { label: string; value: number; format: (v: number) => string }) => (
  <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
    <h4 className="text-sm font-medium text-gray-500">{label}</h4>
    <p className="mt-1 text-2xl font-semibold text-gray-900">{format(value)}</p>
  </div>
);

const PortfolioMetricsComponent: React.FC<Props> = ({ metrics }) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      <MetricCard
        label="总收益"
        value={metrics.total_return}
        format={(v) => `${(v * 100).toFixed(2)}%`}
      />
      <MetricCard
        label="年化收益"
        value={metrics.annual_return}
        format={(v) => `${(v * 100).toFixed(2)}%`}
      />
      <MetricCard
        label="波动率"
        value={metrics.volatility}
        format={(v) => `${(v * 100).toFixed(2)}%`}
      />
      <MetricCard
        label="夏普比率"
        value={metrics.sharpe_ratio}
        format={(v) => v.toFixed(2)}
      />
      <MetricCard
        label="最大回撤"
        value={metrics.max_drawdown}
        format={(v) => `${(v * 100).toFixed(2)}%`}
      />
    </div>
  );
};

export default PortfolioMetricsComponent; 