'use client';

import { useState } from 'react';
import type { PortfolioParams } from '@/types';
import { STRATEGY_OPTIONS } from '@/types/strategy';

interface Props {
  onSubmit: (params: PortfolioParams) => void;
  isLoading: boolean;
}

const PortfolioForm = ({ onSubmit, isLoading }: Props) => {
  const [symbols, setSymbols] = useState<string[]>(['']);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [riskFreeRate, setRiskFreeRate] = useState(0.02);
  const [targetReturn, setTargetReturn] = useState(0.1);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
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
    <form onSubmit={handleSubmit} className="space-y-4 mb-8">
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          股票代码列表
        </label>
        {symbols.map((symbol, index) => (
          <div key={index} className="flex gap-2">
            <input
              type="text"
              value={symbol}
              onChange={(e) => handleSymbolChange(index, e.target.value)}
              className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="输入股票代码"
              required
            />
            <button
              type="button"
              onClick={() => handleRemoveSymbol(index)}
              className="px-3 py-2 text-sm font-medium text-red-600 hover:text-red-700"
            >
              删除
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={handleAddSymbol}
          className="text-blue-600 hover:text-blue-700 text-sm font-medium"
        >
          + 添加股票
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="startDate" className="block text-sm font-medium text-gray-700">
            开始日期
          </label>
          <input
            type="date"
            id="startDate"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            required
          />
        </div>
        <div>
          <label htmlFor="endDate" className="block text-sm font-medium text-gray-700">
            结束日期
          </label>
          <input
            type="date"
            id="endDate"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="riskFreeRate" className="block text-sm font-medium text-gray-700">
            无风险利率 (%)
          </label>
          <input
            type="number"
            id="riskFreeRate"
            value={riskFreeRate * 100}
            onChange={(e) => setRiskFreeRate(parseFloat(e.target.value) / 100)}
            step="0.1"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            required
          />
        </div>
        <div>
          <label htmlFor="targetReturn" className="block text-sm font-medium text-gray-700">
            目标收益率 (%)
          </label>
          <input
            type="number"
            id="targetReturn"
            value={targetReturn * 100}
            onChange={(e) => setTargetReturn(parseFloat(e.target.value) / 100)}
            step="0.1"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            required
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
      >
        {isLoading ? '优化中...' : '运行优化'}
      </button>
    </form>
  );
};

export default PortfolioForm; 