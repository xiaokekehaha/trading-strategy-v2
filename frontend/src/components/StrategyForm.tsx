'use client';

import React, { useState } from 'react';
import { Strategy } from '@/types/strategy';
import { STRATEGY_CONFIGS } from '@/lib/constants';

interface Props {
  defaultValues?: any;
  onSubmit: (params: any) => void;
  isLoading: boolean;
  onStrategyChange: (strategy: string) => void;
}

const StrategyForm: React.FC<Props> = ({
  defaultValues,
  onSubmit,
  isLoading,
  onStrategyChange
}) => {
  // 设置默认日期范围
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);
  const defaultEndDate = yesterday.toISOString().split('T')[0];

  const defaultStartDate = new Date(yesterday);
  defaultStartDate.setDate(yesterday.getDate() - 90);

  const [formData, setFormData] = useState({
    symbol: defaultValues?.symbol || 'AAPL',
    startDate: defaultValues?.startDate || defaultStartDate.toISOString().split('T')[0],
    endDate: defaultValues?.endDate || defaultEndDate,
    strategy: defaultValues?.strategy?.name || 'bollinger_bands',
    params: defaultValues?.strategy?.params || STRATEGY_CONFIGS['bollinger_bands'].params
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      symbol: formData.symbol,
      startDate: formData.startDate,
      endDate: formData.endDate,
      strategy: {
        name: formData.strategy,
        params: formData.params
      }
    });
  };

  const handleStrategyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newStrategy = e.target.value as Strategy;
    const defaultParams = STRATEGY_CONFIGS[newStrategy].params;
    
    setFormData(prev => ({
      ...prev,
      strategy: newStrategy,
      params: Object.fromEntries(
        Object.entries(defaultParams).map(([key, config]) => [key, config.default])
      )
    }));
    
    onStrategyChange(newStrategy);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* 股票代码输入 */}
      <div>
        <label className="block text-sm font-medium text-gray-200 mb-1">
          股票代码
        </label>
        <input
          type="text"
          value={formData.symbol}
          onChange={(e) => setFormData(prev => ({ ...prev, symbol: e.target.value.toUpperCase() }))}
          className="w-full px-3 py-2 bg-[#2D3748] text-gray-100 border border-gray-600 rounded-lg
                   focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                   placeholder-gray-400"
          placeholder="例如: AAPL"
          required
        />
      </div>

      {/* 日期选择 */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-200 mb-1">
            开始日期
          </label>
          <input
            type="date"
            value={formData.startDate}
            onChange={(e) => setFormData(prev => ({ ...prev, startDate: e.target.value }))}
            max={formData.endDate}
            className="w-full px-3 py-2 bg-[#2D3748] text-gray-100 border border-gray-600 rounded-lg
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-200 mb-1">
            结束日期
          </label>
          <input
            type="date"
            value={formData.endDate}
            onChange={(e) => setFormData(prev => ({ ...prev, endDate: e.target.value }))}
            min={formData.startDate}
            max={defaultEndDate}
            className="w-full px-3 py-2 bg-[#2D3748] text-gray-100 border border-gray-600 rounded-lg
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>
      </div>

      {/* 策略选择 */}
      <div>
        <label className="block text-sm font-medium text-gray-200 mb-1">
          策略选择
        </label>
        <select
          value={formData.strategy}
          onChange={handleStrategyChange}
          className="w-full px-3 py-2 bg-[#2D3748] text-gray-100 border border-gray-600 rounded-lg
                   focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {Object.entries(STRATEGY_CONFIGS).map(([key, config]) => (
            <option key={key} value={key}>
              {config.name}
            </option>
          ))}
        </select>
      </div>

      {/* 策略参数 */}
      <div>
        <label className="block text-sm font-medium text-gray-200 mb-1">
          策略参数
        </label>
        <div className="grid grid-cols-2 gap-4">
          {Object.entries(STRATEGY_CONFIGS[formData.strategy].params).map(([key, config]) => (
            <div key={key}>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                {config.label}
              </label>
              <input
                type="number"
                value={formData.params[key]}
                onChange={(e) => {
                  const value = parseFloat(e.target.value);
                  if (!isNaN(value) && value >= config.min && value <= config.max) {
                    setFormData(prev => ({
                      ...prev,
                      params: {
                        ...prev.params,
                        [key]: value
                      }
                    }));
                  }
                }}
                step={config.step}
                min={config.min}
                max={config.max}
                className="w-full px-3 py-2 bg-[#2D3748] text-gray-100 border border-gray-600 rounded-lg
                         focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          ))}
        </div>
      </div>

      {/* 提交按钮 */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 
                 text-white font-medium rounded-lg
                 transition-colors duration-200
                 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? '回测中...' : '开始回测'}
      </button>
    </form>
  );
};

export default StrategyForm; 