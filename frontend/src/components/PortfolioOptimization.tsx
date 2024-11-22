'use client';

import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import type { PortfolioAnalysisResult } from '@/types/portfolio';
import api from '@/lib/api';

interface Props {
  onOptimized: (result: PortfolioAnalysisResult) => void;
}

const PortfolioOptimization: React.FC<Props> = ({ onOptimized }) => {
  const [symbols, setSymbols] = useState<string[]>(['']);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [riskFreeRate, setRiskFreeRate] = useState(0.02);
  const [targetReturn, setTargetReturn] = useState<number | undefined>();

  const { mutate: optimizePortfolio, isPending } = useMutation({
    mutationFn: async (data: {
      symbols: string[];
      startDate: string;
      endDate: string;
      riskFreeRate: number;
      targetReturn?: number;
    }) => {
      const { data: result } = await api.post<PortfolioAnalysisResult>(
        '/api/portfolio/optimize',
        data
      );
      return result;
    },
    onSuccess: onOptimized
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    optimizePortfolio({
      symbols: symbols.filter(Boolean),
      startDate,
      endDate,
      riskFreeRate,
      targetReturn
    });
  };

  const handleAddSymbol = () => {
    setSymbols([...symbols, '']);
  };

  const handleRemoveSymbol = (index: number) => {
    setSymbols(symbols.filter((_, i) => i !== index));
  };

  const handleSymbolChange = (index: number, value: string) => {
    const newSymbols = [...symbols];
    newSymbols[index] = value;
    setSymbols(newSymbols);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-4">
        {symbols.map((symbol, index) => (
          <div key={index} className="flex gap-4">
            <input
              type="text"
              value={symbol}
              onChange={(e) => handleSymbolChange(index, e.target.value)}
              placeholder="股票代码"
              className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
            <button
              type="button"
              onClick={() => handleRemoveSymbol(index)}
              className="px-3 py-2 text-sm text-red-600 hover:text-red-700"
            >
              删除
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={handleAddSymbol}
          className="text-blue-600 hover:text-blue-700"
        >
          添加股票
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">开始日期</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">结束日期</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">无风险利率</label>
        <input
          type="number"
          value={riskFreeRate}
          onChange={(e) => setRiskFreeRate(parseFloat(e.target.value))}
          step="0.001"
          min="0"
          max="1"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">目标收益率（可选）</label>
        <input
          type="number"
          value={targetReturn ?? ''}
          onChange={(e) => setTargetReturn(e.target.value ? parseFloat(e.target.value) : undefined)}
          step="0.01"
          min="0"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <button
        type="submit"
        disabled={isPending || symbols.filter(Boolean).length === 0}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
      >
        {isPending ? '优化中...' : '开始优化'}
      </button>
    </form>
  );
};

export default PortfolioOptimization; 