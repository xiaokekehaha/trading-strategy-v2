'use client';

import React from 'react';
import type { StrategyMetrics as StrategyMetricsType } from '@/types';

interface Props {
  metrics: StrategyMetricsType;
}

const MetricCard = ({ 
  title, 
  value, 
  baseline, 
  description 
}: { 
  title: string; 
  value: string; 
  baseline: string;
  description: string;
}) => (
  <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
    <div className="flex justify-between items-start mb-2">
      <h3 className="text-gray-500 text-sm">{title}</h3>
      <span className="text-gray-400 text-xs">{baseline}</span>
    </div>
    <p className="text-3xl font-bold text-blue-600 mb-1">
      {value}
    </p>
    <p className="text-xs text-gray-500">
      {description}
    </p>
  </div>
);

const StrategyMetricsComponent: React.FC<Props> = ({ metrics }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <MetricCard
        title="策略在整个回测期间的累计收益率"
        value={`${(metrics.total_return * 100).toFixed(2)}%`}
        baseline="基准: 沪深300: 10%/年"
        description="总收益率"
      />
      <MetricCard
        title="将总收益率转换为年化基准的收益率"
        value={`${(metrics.annual_return * 100).toFixed(2)}%`}
        baseline="基准: 沪深300: 8-12%"
        description="年化收益率"
      />
      <MetricCard
        title="收益率的标准差，反映策略的风险水平"
        value={`${(metrics.sharpe_ratio).toFixed(2)}`}
        baseline="基准: 行业均值: 15-20%"
        description="夏普比率"
      />
      <MetricCard
        title="最大的净值回撤幅度，反映策略的下行风险"
        value={`${(metrics.max_drawdown * 100).toFixed(2)}%`}
        baseline="基准: 行业标准: <20%"
        description="最大回撤"
      />
      <MetricCard
        title="超额收益与波动率的比值，衡量风险调整后的收益"
        value={`${(metrics.win_rate * 100).toFixed(2)}%`}
        baseline="基准: 胜率基准: >50%"
        description="胜率"
      />
      <MetricCard
        title="总交易次数"
        value={metrics.total_trades.toString()}
        baseline="基准: 股票基金: >50%"
        description="交易统计"
      />
    </div>
  );
};

export default StrategyMetricsComponent; 