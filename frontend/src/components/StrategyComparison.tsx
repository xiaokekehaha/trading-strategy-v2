'use client';

import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface Strategy {
  name: string;
  metrics: {
    annual_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    win_rate: number;
  };
}

interface Props {
  strategies: Strategy[];
}

const StrategyComparison: React.FC<Props> = ({ strategies }) => {
  const data = {
    labels: strategies.map(s => s.name),
    datasets: [
      {
        label: '年化收益率',
        data: strategies.map(s => s.metrics.annual_return * 100),
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
      },
      {
        label: '夏普比率',
        data: strategies.map(s => s.metrics.sharpe_ratio),
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
      },
      {
        label: '最大回撤',
        data: strategies.map(s => s.metrics.max_drawdown * 100),
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
      {
        label: '胜率',
        data: strategies.map(s => s.metrics.win_rate * 100),
        backgroundColor: 'rgba(153, 102, 255, 0.5)',
      }
    ]
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: '策略对比分析'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value: number) => `${value.toFixed(2)}%`
        }
      }
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
      <Bar options={options} data={data} />
    </div>
  );
};

export default StrategyComparison; 