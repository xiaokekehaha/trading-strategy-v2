'use client';

import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions
} from 'chart.js';
import { formatPercentage } from '@/lib/utils';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface ChartData {
  date: string;
  value: number;
}

interface Props {
  returns: ChartData[];
  drawdown: ChartData[];
  metrics: {
    total_return: number;
    annual_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    win_rate: number;
    volatility: number;
  };
}

export const PortfolioCharts: React.FC<Props> = ({
  returns,
  drawdown,
  metrics
}) => {
  const options: ChartOptions<'line'> = {
    responsive: true,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += formatPercentage(context.parsed.y);
            }
            return label;
          }
        }
      }
    },
    scales: {
      x: {
        type: 'category',
        display: true,
        title: {
          display: true,
          text: '日期'
        },
        ticks: {
          maxTicksLimit: 10
        }
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: '收益率'
        },
        ticks: {
          callback: function(value) {
            return formatPercentage(value as number);
          }
        }
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: '回撤'
        },
        ticks: {
          callback: function(value) {
            return formatPercentage(value as number);
          }
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  const data = {
    labels: returns.map(d => d.date),
    datasets: [
      {
        label: '累计收益',
        data: returns.map(d => d.value),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        yAxisID: 'y',
        fill: true,
      },
      {
        label: '回撤',
        data: drawdown.map(d => d.value),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        yAxisID: 'y1',
        fill: true,
      }
    ],
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <MetricCard
          label="总收益率"
          value={metrics.total_return}
          trend={metrics.total_return > 0 ? 'up' : 'down'}
        />
        <MetricCard
          label="年化收益"
          value={metrics.annual_return}
          trend={metrics.annual_return > 0 ? 'up' : 'down'}
        />
        <MetricCard
          label="夏普比率"
          value={metrics.sharpe_ratio}
          trend={metrics.sharpe_ratio > 1 ? 'up' : 'down'}
          format={(v) => v.toFixed(2)}
        />
        <MetricCard
          label="最大回撤"
          value={metrics.max_drawdown}
          trend="down"
        />
        <MetricCard
          label="胜率"
          value={metrics.win_rate}
        />
        <MetricCard
          label="波动率"
          value={metrics.volatility}
          trend={metrics.volatility > 0.2 ? 'down' : undefined}
        />
      </div>
      
      <div className="bg-white p-4 rounded-lg shadow">
        <Line options={options} data={data} height={80} />
      </div>
    </div>
  );
};

interface MetricCardProps {
  label: string;
  value: number;
  trend?: 'up' | 'down';
  format?: (value: number) => string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  trend,
  format = formatPercentage
}) => {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="text-sm text-gray-500 mb-1">{label}</div>
      <div className={`text-xl font-semibold ${
        trend === 'up' ? 'text-green-600' :
        trend === 'down' ? 'text-red-600' :
        'text-gray-900'
      }`}>
        {format(value)}
        {trend && (
          <span className="ml-2">
            {trend === 'up' ? '↑' : '↓'}
          </span>
        )}
      </div>
    </div>
  );
}; 