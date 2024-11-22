'use client';

import React from 'react';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

interface Props {
  allocation: Record<string, number>;
}

const PortfolioAllocationComponent: React.FC<Props> = ({ allocation }) => {
  const data = {
    labels: Object.keys(allocation),
    datasets: [
      {
        data: Object.values(allocation).map(v => v * 100),
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
          '#9966FF',
          '#FF9F40',
          '#FF99CC',
        ],
      },
    ],
  };

  const options = {
    plugins: {
      legend: {
        position: 'right' as const,
      },
      title: {
        display: true,
        text: '投资组合配置',
      },
    },
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
      <h3 className="text-lg font-medium text-gray-900 mb-4">资产配置</h3>
      <div className="h-64">
        <Pie data={data} options={options} />
      </div>
      <div className="mt-4 space-y-2">
        {Object.entries(allocation).map(([symbol, weight]) => (
          <div key={symbol} className="flex justify-between items-center">
            <span className="text-sm text-gray-600">{symbol}</span>
            <span className="text-sm font-medium">{(weight * 100).toFixed(2)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PortfolioAllocationComponent; 