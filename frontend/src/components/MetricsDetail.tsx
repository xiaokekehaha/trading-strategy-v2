'use client';

import { useMemo } from 'react';
import type { StrategyMetrics } from '@/types';

interface MetricDetailCardProps {
  label: string;
  value: number;
  format?: (value: number) => string;
  description: string;
  trend?: 'up' | 'down';
  benchmark?: string;
  analysis: string;
}

const MetricDetailCard = ({
  label,
  value,
  format,
  description,
  trend,
  benchmark,
  analysis
}: MetricDetailCardProps) => {
  const formattedValue = format ? format(value) : value.toFixed(2);
  const trendColor = trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600';

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold text-gray-800">{label}</h3>
        <span className={`text-2xl font-bold ${trendColor}`}>
          {formattedValue}
        </span>
      </div>
      <div className="space-y-3">
        <p className="text-sm text-gray-600">{description}</p>
        {benchmark && (
          <p className="text-sm text-gray-500">
            <span className="font-medium">基准参考：</span>{benchmark}
          </p>
        )}
        <p className="text-sm text-gray-700">
          <span className="font-medium">分析：</span>{analysis}
        </p>
      </div>
    </div>
  );
};

interface Props {
  metrics: StrategyMetrics;
}

const MetricsDetail = ({ metrics }: Props) => {
  const formatPercentage = (value: number) => `${(value * 100).toFixed(2)}%`;
  const formatRatio = (value: number) => value.toFixed(2);

  const annualizedReturn = useMemo(() => {
    return metrics.annualReturn * 100;
  }, [metrics.annualReturn]);

  return (
    <div className="space-y-8">
      <div className="bg-white p-6 rounded-lg shadow mb-8">
        <h2 className="text-2xl font-bold mb-4">策略绩效分析报告</h2>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium">分析周期：</span>
            <span className="text-gray-600">全周期</span>
          </div>
          <div>
            <span className="font-medium">交易次数：</span>
            <span className="text-gray-600">{metrics.totalTrades || 0} 次</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <MetricDetailCard
          label="总收益率"
          value={metrics.totalReturn}
          format={formatPercentage}
          trend={metrics.totalReturn > 0 ? 'up' : 'down'}
          description="策略在整个回测期间的累计收益率"
          benchmark="市场基准：10%/年"
          analysis={`总收益率${metrics.totalReturn > 0.1 ? '优于' : '低于'}市场平均水平`}
        />

        <MetricDetailCard
          label="年化收益率"
          value={metrics.annualReturn}
          format={formatPercentage}
          trend={metrics.annualReturn > 0 ? 'up' : 'down'}
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
          value={metrics.sharpeRatio}
          format={formatRatio}
          trend={metrics.sharpeRatio > 1 ? 'up' : 'down'}
          description="超额收益与波动率的比值，衡量风险调整后的收益"
          benchmark="市场基准：>1.0"
          analysis={`夏普比率${metrics.sharpeRatio > 1.5 ? '优秀' : metrics.sharpeRatio > 1 ? '良好' : '需要改进'}`}
        />

        <MetricDetailCard
          label="最大回撤"
          value={metrics.maxDrawdown}
          format={formatPercentage}
          trend="down"
          description="最大的净值回撤幅度，反映策略的下行风险"
          benchmark="市场基准：<20%"
          analysis={`最大回撤${metrics.maxDrawdown < 0.2 ? '在可接受范围内' : '风险较高'}`}
        />

        <MetricDetailCard
          label="胜率"
          value={metrics.winRate || 0}
          format={formatPercentage}
          trend={(metrics.winRate || 0) > 0.5 ? 'up' : 'down'}
          description="盈利交易占总交易次数的比例"
          benchmark="市场基准：>50%"
          analysis={`交易胜率${(metrics.winRate || 0) > 0.5 ? '良好' : '需要优化'}`}
        />
      </div>
    </div>
  );
};

export default MetricsDetail; 