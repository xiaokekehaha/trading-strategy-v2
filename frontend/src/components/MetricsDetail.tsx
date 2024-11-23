'use client';

import React, { useMemo } from 'react';
import { StrategyMetrics } from '@/types/backtest';
import { formatPercentage, formatRatio } from '@/lib/utils';

interface Props {
  metrics: StrategyMetrics;
}

const MetricDetailCard = ({
  label,
  value,
  format,
  trend,
  description,
  benchmark,
  analysis
}: {
  label: string;
  value: number;
  format: (value: number) => string;
  trend?: 'up' | 'down';
  description: string;
  benchmark: string;
  analysis: string;
}) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h4 className="text-lg font-semibold text-gray-900">{label}</h4>
          <p className="text-sm text-gray-500">{description}</p>
        </div>
        <span className={`text-2xl font-bold ${trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-900'}`}>
          {format(value)}
        </span>
      </div>
      <div className="space-y-2">
        <p className="text-sm text-gray-600">
          <span className="font-medium">基准: </span>
          {benchmark}
        </p>
        <p className="text-sm text-gray-600">
          <span className="font-medium">分析: </span>
          {analysis}
        </p>
      </div>
    </div>
  );
};

const MetricsDetail: React.FC<Props> = ({ metrics }) => {
  const annualizedReturn = useMemo(() => {
    return metrics.annual_return * 100;
  }, [metrics.annual_return]);

  return (
    <div className="space-y-8">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">基本指标</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <span className="font-medium">交易次数：</span>
            <span className="text-gray-600">{metrics.total_trades || 0} 次</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <MetricDetailCard
          label="总收益率"
          value={metrics.total_return}
          format={formatPercentage}
          trend={metrics.total_return > 0 ? 'up' : 'down'}
          description="策略在整个回测期间的累计收益率"
          benchmark="市场基准：10%/年"
          analysis={`总收益率${metrics.total_return > 0.1 ? '优于' : '低于'}市场平均水平`}
        />

        <MetricDetailCard
          label="年化收益率"
          value={metrics.annual_return}
          format={formatPercentage}
          trend={metrics.annual_return > 0 ? 'up' : 'down'}
          description="将总收益率转换为年化基准的收益率"
          benchmark="市场基准：8-12%"
          analysis={`年化收益${annualizedReturn > 12 ? '显著高于' : annualizedReturn > 8 ? '接近' : '低于'}市场水平`}
        />

        <MetricDetailCard
          label="波动率"
          value={metrics.volatility}
          format={formatPercentage}
          description="收益率的标准差，反映策略的风险水平"
          benchmark="市场基准：15-20%"
          analysis={`策略波动率${metrics.volatility < 0.15 ? '低于' : metrics.volatility > 0.2 ? '高于' : '处于'}正常范围`}
        />

        <MetricDetailCard
          label="夏普比率"
          value={metrics.sharpe_ratio}
          format={formatRatio}
          trend={metrics.sharpe_ratio > 1 ? 'up' : 'down'}
          description="超额收益与波动率的比值，衡量风险调整后的收益"
          benchmark="市场基准：>1.0"
          analysis={`夏普比率${metrics.sharpe_ratio > 1.5 ? '优秀' : metrics.sharpe_ratio > 1 ? '良好' : '需要改进'}`}
        />

        <MetricDetailCard
          label="最大回撤"
          value={metrics.max_drawdown}
          format={formatPercentage}
          trend="down"
          description="最大的净值回撤幅度，反映策略的下行风险"
          benchmark="市场基准：<20%"
          analysis={`最大回撤${metrics.max_drawdown < 0.2 ? '在可接受范围内' : '风险较高'}`}
        />

        <MetricDetailCard
          label="胜率"
          value={metrics.win_rate}
          format={formatPercentage}
          trend={metrics.win_rate > 0.5 ? 'up' : 'down'}
          description="盈利交易占总交易次数的比例"
          benchmark="市场基准：>50%"
          analysis={`交易胜率${metrics.win_rate > 0.5 ? '良好' : '需要优化'}`}
        />
      </div>
    </div>
  );
};

export default MetricsDetail; 