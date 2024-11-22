import React from 'react';
import { OptimizationFormData } from '../types/portfolio';

interface FormProps {
  onSubmit: (data: OptimizationFormData) => void;
  isLoading: boolean;
}

export const OptimizationForm: React.FC<FormProps> = ({ onSubmit, isLoading }) => {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    
    const data: OptimizationFormData = {
      symbols: formData.get('symbols') as string,
      lookback_years: parseInt(formData.get('lookback_years') as string),
      target_return: parseFloat(formData.get('target_return') as string),
      risk_free_rate: parseFloat(formData.get('risk_free_rate') as string)
    };

    if (!data.symbols || !data.symbols.trim()) {
      alert('请输入股票代码');
      return;
    }

    if (isNaN(data.lookback_years) || data.lookback_years < 1 || data.lookback_years > 10) {
      alert('回溯期必须在1-10年之间');
      return;
    }

    if (isNaN(data.target_return) || data.target_return <= 0) {
      alert('请输入有效的目标收益率');
      return;
    }

    if (isNaN(data.risk_free_rate) || data.risk_free_rate < 0) {
      alert('请输入有效的无风险利率');
      return;
    }

    onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="symbols" className="block text-sm font-medium text-gray-700">
          股票代码 (用逗号分隔)
        </label>
        <input
          type="text"
          name="symbols"
          id="symbols"
          defaultValue="AAPL,MSFT,GOOGL,AMZN,META"
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
        <p className="mt-1 text-sm text-gray-500">例如: AAPL,MSFT,GOOGL</p>
      </div>

      <div>
        <label htmlFor="lookback_years" className="block text-sm font-medium text-gray-700">
          回溯期(年)
        </label>
        <input
          type="number"
          name="lookback_years"
          id="lookback_years"
          defaultValue={5}
          min={1}
          max={10}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div>
        <label htmlFor="target_return" className="block text-sm font-medium text-gray-700">
          目标收益率 (%)
        </label>
        <input
          type="number"
          name="target_return"
          id="target_return"
          defaultValue={10.0}
          step={0.1}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div>
        <label htmlFor="risk_free_rate" className="block text-sm font-medium text-gray-700">
          无风险利率 (%)
        </label>
        <input
          type="number"
          name="risk_free_rate"
          id="risk_free_rate"
          defaultValue={2.0}
          step={0.1}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="inline-flex justify-center rounded-md border border-transparent bg-blue-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
      >
        {isLoading ? '优化中...' : '开始优化'}
      </button>
    </form>
  );
}; 