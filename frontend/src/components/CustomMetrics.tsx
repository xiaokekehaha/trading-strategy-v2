'use client';

import React, { useState } from 'react';
import { evaluate } from 'mathjs';
import type { BacktestResult } from '@/types';

interface CustomMetric {
  name: string;
  formula: string;
  description: string;
}

interface Props {
  result: BacktestResult;
}

const CustomMetrics: React.FC<Props> = ({ result }) => {
  const [metrics, setMetrics] = useState<CustomMetric[]>([]);
  const [newMetric, setNewMetric] = useState<CustomMetric>({
    name: '',
    formula: '',
    description: ''
  });

  const calculateMetric = (formula: string): number => {
    try {
      const scope = {
        returns: result.metrics.annual_return,
        volatility: result.metrics.volatility,
        drawdown: result.metrics.max_drawdown,
        trades: result.metrics.total_trades,
        winRate: result.metrics.win_rate
      };
      return evaluate(formula, scope);
    } catch (e) {
      console.error('计算指标失败:', e);
      return NaN;
    }
  };

  const handleAddMetric = () => {
    if (newMetric.name && newMetric.formula) {
      setMetrics([...metrics, newMetric]);
      setNewMetric({ name: '', formula: '', description: '' });
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium text-gray-900 mb-4">自定义指标分析</h3>
      
      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            指标名称
          </label>
          <input
            type="text"
            value={newMetric.name}
            onChange={(e) => setNewMetric({ ...newMetric, name: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">
            计算公式
          </label>
          <input
            type="text"
            value={newMetric.formula}
            onChange={(e) => setNewMetric({ ...newMetric, formula: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="例如: returns / volatility"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">
            指标说明
          </label>
          <textarea
            value={newMetric.description}
            onChange={(e) => setNewMetric({ ...newMetric, description: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            rows={2}
          />
        </div>
        
        <button
          onClick={handleAddMetric}
          className="px-4 py-2 rounded-md bg-blue-100 text-blue-700 hover:bg-blue-200"
        >
          添加指标
        </button>
      </div>
      
      <div className="space-y-4">
        {metrics.map((metric, index) => (
          <div key={index} className="border rounded-lg p-4">
            <h4 className="font-medium text-gray-900">{metric.name}</h4>
            <p className="text-sm text-gray-500 mt-1">{metric.description}</p>
            <p className="text-sm text-gray-600 mt-1">公式: {metric.formula}</p>
            <p className="text-lg font-semibold text-gray-900 mt-2">
              {calculateMetric(metric.formula).toFixed(4)}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CustomMetrics; 