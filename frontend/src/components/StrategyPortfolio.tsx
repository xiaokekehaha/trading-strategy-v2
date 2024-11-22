'use client';

import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import api from '@/lib/api';

interface Strategy {
  name: string;
  weight: number;
  params: Record<string, number>;
}

interface Props {
  availableStrategies: string[];
  onOptimized: (result: any) => void;
}

const StrategyPortfolio: React.FC<Props> = ({ availableStrategies, onOptimized }) => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [optimizationTarget, setOptimizationTarget] = useState<'sharpe' | 'returns'>('sharpe');

  const { mutate: optimizePortfolio, isPending } = useMutation({
    mutationFn: async (data: {
      strategies: Strategy[];
      target: string;
    }) => {
      const { data: result } = await api.post('/api/portfolio/optimize', data);
      return result;
    },
    onSuccess: onOptimized
  });

  const handleAddStrategy = () => {
    setStrategies([
      ...strategies,
      {
        name: availableStrategies[0],
        weight: 0,
        params: {}
      }
    ]);
  };

  const handleRemoveStrategy = (index: number) => {
    setStrategies(strategies.filter((_, i) => i !== index));
  };

  const handleStrategyChange = (index: number, field: keyof Strategy, value: any) => {
    setStrategies(strategies.map((strategy, i) => 
      i === index ? { ...strategy, [field]: value } : strategy
    ));
  };

  const handleOptimize = () => {
    optimizePortfolio({
      strategies,
      target: optimizationTarget
    });
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">策略组合优化</h3>
        
        <div className="space-y-4">
          {strategies.map((strategy, index) => (
            <div key={index} className="flex items-center gap-4">
              <select
                value={strategy.name}
                onChange={(e) => handleStrategyChange(index, 'name', e.target.value)}
                className="block w-48 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                {availableStrategies.map(name => (
                  <option key={name} value={name}>{name}</option>
                ))}
              </select>
              
              <input
                type="number"
                min="0"
                max="1"
                step="0.1"
                value={strategy.weight}
                onChange={(e) => handleStrategyChange(index, 'weight', parseFloat(e.target.value))}
                className="block w-24 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
              
              <button
                onClick={() => handleRemoveStrategy(index)}
                className="px-3 py-1 rounded-md bg-red-100 text-red-700 hover:bg-red-200"
              >
                删除
              </button>
            </div>
          ))}
          
          <button
            onClick={handleAddStrategy}
            className="px-4 py-2 rounded-md bg-blue-100 text-blue-700 hover:bg-blue-200"
          >
            添加策略
          </button>
        </div>
        
        <div className="mt-6">
          <label className="block text-sm font-medium text-gray-700">
            优化目标
          </label>
          <select
            value={optimizationTarget}
            onChange={(e) => setOptimizationTarget(e.target.value as 'sharpe' | 'returns')}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="sharpe">最大化夏普比率</option>
            <option value="returns">最大化收益率</option>
          </select>
        </div>
        
        <button
          onClick={handleOptimize}
          disabled={isPending || strategies.length === 0}
          className="mt-6 w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {isPending ? '优化中...' : '开始优化'}
        </button>
      </div>
    </div>
  );
};

export default StrategyPortfolio; 