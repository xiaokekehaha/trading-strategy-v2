'use client';

import React, { useState } from 'react';
import type { BacktestParams } from '@/types';
import type { Strategy } from '@/types/strategy';

interface Props {
  onSubmit: (params: BacktestParams) => void;
  isLoading: boolean;
  onStrategyChange: (strategy: string) => void;
}

interface StrategyParamConfig {
  label: string;
  min: number;
  max: number;
  step: number;
  default: number;
}

const STRATEGY_CONFIGS = {
  'bollinger_bands': {
    name: '布林带策略',
    params: {
      window: {
        label: '移动窗口',
        min: 5,
        max: 100,
        step: 1,
        default: 20
      },
      num_std: {
        label: '标准差倍数',
        min: 0.1,
        max: 5.0,
        step: 0.1,
        default: 2.0
      }
    }
  },
  'macd': {
    name: 'MACD策略',
    params: {
      fast_period: {
        label: '快速周期',
        min: 3,
        max: 50,
        step: 1,
        default: 12
      },
      slow_period: {
        label: '慢速周期',
        min: 5,
        max: 100,
        step: 1,
        default: 26
      },
      signal_period: {
        label: '信号周期',
        min: 3,
        max: 50,
        step: 1,
        default: 9
      }
    }
  },
  'moving_average': {
    name: '移动平均策略',
    params: {
      short_window: {
        label: '短期窗口',
        min: 2,
        max: 50,
        step: 1,
        default: 5
      },
      long_window: {
        label: '长期窗口',
        min: 5,
        max: 200,
        step: 1,
        default: 20
      }
    }
  },
  'svm': {
    name: 'SVM策略',
    params: {
      lookback_period: {
        label: '回看周期',
        min: 5,
        max: 100,
        step: 1,
        default: 20
      },
      C: {
        label: '正则化参数',
        min: 0.1,
        max: 10.0,
        step: 0.1,
        default: 1.0
      },
      gamma: {
        label: 'Gamma参数',
        min: 0.001,
        max: 1.0,
        step: 0.001,
        default: 0.1
      }
    }
  },
  'random_forest': {
    name: '随机森林策略',
    params: {
      lookback_period: {
        label: '回看周期',
        min: 5,
        max: 100,
        step: 1,
        default: 20
      },
      n_estimators: {
        label: '树的数量',
        min: 10,
        max: 500,
        step: 10,
        default: 100
      },
      max_depth: {
        label: '最大深度',
        min: 3,
        max: 20,
        step: 1,
        default: 10
      }
    }
  },
  'xgboost': {
    name: 'XGBoost策略',
    params: {
      lookback_period: {
        label: '回看周期',
        min: 5,
        max: 100,
        step: 1,
        default: 20
      },
      n_estimators: {
        label: '迭代次数',
        min: 10,
        max: 500,
        step: 10,
        default: 100
      },
      learning_rate: {
        label: '学习率',
        min: 0.001,
        max: 1.0,
        step: 0.001,
        default: 0.1
      },
      max_depth: {
        label: '最大深度',
        min: 3,
        max: 10,
        step: 1,
        default: 6
      }
    }
  },
  'lstm': {
    name: 'LSTM策略',
    params: {
      lookback_period: {
        label: '回看周期',
        min: 5,
        max: 100,
        step: 1,
        default: 20
      },
      units: {
        label: '神经元数量',
        min: 10,
        max: 200,
        step: 10,
        default: 50
      },
      epochs: {
        label: '训练轮数',
        min: 10,
        max: 500,
        step: 10,
        default: 100
      },
      batch_size: {
        label: '批次大小',
        min: 8,
        max: 128,
        step: 8,
        default: 32
      },
      dropout: {
        label: 'Dropout率',
        min: 0.1,
        max: 0.5,
        step: 0.1,
        default: 0.2
      }
    }
  }
} as const;

const StrategyForm = ({ onSubmit, isLoading, onStrategyChange }: Props) => {
  // 设置默认日期范围：结束日期为昨天，开始日期为90天前
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);
  const defaultEndDate = yesterday.toISOString().split('T')[0];

  const defaultStartDate = new Date(yesterday);
  defaultStartDate.setDate(yesterday.getDate() - 90);  // 默认90天回测周期
  
  const [symbol, setSymbol] = useState('');
  const [startDate, setStartDate] = useState(defaultStartDate.toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState(defaultEndDate);
  const [strategy, setStrategy] = useState<Strategy>('bollinger_bands');
  const [params, setParams] = useState<Record<string, number>>({
    window: 20,
    num_std: 2.0
  });

  const validateDates = () => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const today = new Date();
    
    // 检查日期范围
    if (start > end) {
      throw new Error('开始日期不能晚于结束日期');
    }
    
    if (end > today) {
      throw new Error('结束日期不能晚于今天');
    }
    
    // 检查是否为工作日
    const isWeekend = (date: Date) => date.getDay() === 0 || date.getDay() === 6;
    if (isWeekend(start) || isWeekend(end)) {
      throw new Error('请选择工作日进行回测');
    }
    
    // 确保至少有30天的数据
    const daysDiff = Math.floor((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
    if (daysDiff < 30) {
      throw new Error('请选择至少30天的回测周期');
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      validateDates();
      onSubmit({
        symbol,
        startDate,
        endDate,
        strategy: {
          name: strategy,
          params
        }
      });
    } catch (error) {
      alert(error instanceof Error ? error.message : '日期验证失败');
    }
  };

  const handleStrategyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newStrategy = e.target.value as Strategy;
    setStrategy(newStrategy);
    onStrategyChange(newStrategy);
    
    // 设置默认参数
    const defaultParams: Record<string, number> = {};
    const strategyConfig = STRATEGY_CONFIGS[newStrategy];
    Object.entries(strategyConfig.params).forEach(([key, config]) => {
      defaultParams[key] = config.default;
    });
    setParams(defaultParams);
  };

  const handleParamChange = (paramName: string, value: string) => {
    const newValue = parseFloat(value);
    const config = STRATEGY_CONFIGS[strategy].params[paramName];
    
    if (!isNaN(newValue) && newValue >= config.min && newValue <= config.max) {
      setParams(prev => ({
        ...prev,
        [paramName]: newValue
      }));
    }
  };

  // 获取最早可选日期（当前日期往前推5年）
  const minDate = new Date();
  minDate.setFullYear(minDate.getFullYear() - 5);
  
  // 获取最晚可选日期（昨天）
  const maxDate = yesterday;

  return (
    <form onSubmit={handleSubmit} className="space-y-4 mb-8">
      <div>
        <label htmlFor="symbol" className="block text-sm font-medium text-gray-700">
          股票代码
        </label>
        <input
          type="text"
          id="symbol"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}  // 自动转换为大写
          placeholder="例如: AAPL, MSFT"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          required
        />
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
            min={minDate.toISOString().split('T')[0]}
            max={maxDate.toISOString().split('T')[0]}
            onChange={(e) => setStartDate(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            required
          />
          <p className="mt-1 text-xs text-gray-500">
            最早可选择5年前的数据
          </p>
        </div>
        <div>
          <label htmlFor="endDate" className="block text-sm font-medium text-gray-700">
            结束日期
          </label>
          <input
            type="date"
            id="endDate"
            value={endDate}
            min={startDate}
            max={maxDate.toISOString().split('T')[0]}
            onChange={(e) => setEndDate(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            required
          />
          <p className="mt-1 text-xs text-gray-500">
            默认为昨天
          </p>
        </div>
      </div>

      <div>
        <label htmlFor="strategy" className="block text-sm font-medium text-gray-700">
          策略类型
        </label>
        <select
          id="strategy"
          value={strategy}
          onChange={handleStrategyChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          {Object.entries(STRATEGY_CONFIGS).map(([value, config]) => (
            <option key={value} value={value}>
              {config.name}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-4">
        {Object.entries(STRATEGY_CONFIGS[strategy].params).map(([paramName, config]) => (
          <div key={paramName}>
            <label htmlFor={paramName} className="block text-sm font-medium text-gray-700">
              {config.label}
            </label>
            <input
              type="number"
              id={paramName}
              min={config.min}
              max={config.max}
              step={config.step}
              value={params[paramName] ?? config.default}
              onChange={(e) => handleParamChange(paramName, e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
        ))}
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
      >
        {isLoading ? '运行中...' : '运行回测'}
      </button>
    </form>
  );
};

export default StrategyForm; 