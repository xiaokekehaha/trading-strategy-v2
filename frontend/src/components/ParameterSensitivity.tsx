'use client';

import React, { useMemo } from 'react';
import { Line } from 'react-chartjs-2';
import type { BacktestResult } from '@/types';

interface Props {
  results: BacktestResult[];
  paramName: string;
  paramValues: number[];
}

const ParameterSensitivity: React.FC<Props> = ({ results, paramName, paramValues }) => {
  const chartData = useMemo(() => {
    const metrics = ['annual_return', 'sharpe_ratio', 'max_drawdown'];
    const colors = {
      annual_return: 'rgb(75, 192, 192)',
      sharpe_ratio: 'rgb(54, 162, 235)',
      max_drawdown: 'rgb(255, 99, 132)'
    };

    return {
      labels: paramValues,
      datasets: metrics.map(metric => ({
        label: metric === 'annual_return' ? '年化收益率' :
               metric === 'sharpe_ratio' ? '夏普比率' : '最大回撤',
        data: results.map(r => r.metrics[metric] * (metric === 'max_drawdown' ? -1 : 1)),
        borderColor: colors[metric],
        fill: false,
        tension: 0.4
      }))
    };
  }, [results, paramValues]);

  const options = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: `参数敏感性分析: ${paramName}`
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const value = context.parsed.y;
            return `${context.dataset.label}: ${(value * 100).toFixed(2)}%`;
          }
        }
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: paramName
        }
      },
      y: {
        title: {
          display: true,
          text: '指标值'
        },
        ticks: {
          callback: (value) => `${(value * 100).toFixed(1)}%`
        }
      }
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium text-gray-900 mb-4">参数敏感性分析</h3>
      <Line data={chartData} options={options} />
      <div className="mt-4 space-y-2">
        <p className="text-sm text-gray-600">
          参数敏感性分析显示了策略参数变化对主要指标的影响。通过观察曲线的斜率和趋势，
          可以判断策略对参数变化的敏感程度，从而选择最优参数区间。
        </p>
        <ul className="text-sm text-gray-600 list-disc list-inside">
          <li>较平缓的曲线表示策略对该参数不敏感，参数选择范围较大</li>
          <li>陡峭的曲线表示��略对该参数敏感，需要谨慎选择参数值</li>
          <li>曲线的拐点可能是参数的最优选择区域</li>
        </ul>
      </div>
    </div>
  );
};

export default ParameterSensitivity; 