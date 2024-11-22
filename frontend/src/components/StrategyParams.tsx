'use client';

import React from 'react';
import type { Strategy } from '@/types/strategy';

interface Props {
  strategy: Strategy;
  onChange: (params: Record<string, number>) => void;
}

interface StrategyParamConfig {
  label: string;
  min: number;
  max: number;
  step: number;
  default: number;
}

type StrategyParamsConfig = Record<string, Record<string, StrategyParamConfig>>;

const PARAMS_CONFIG: StrategyParamsConfig = {
  'moving_average': {
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
  },
  'bollinger_bands': {
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
  },
  'macd': {
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
};

const StrategyParams: React.FC<Props> = ({ strategy, onChange }) => {
  const params = PARAMS_CONFIG[strategy] || {};

  const handleParamChange = (paramName: string, value: string) => {
    const newValue = parseFloat(value);
    const config = params[paramName];
    
    if (config && !isNaN(newValue) && newValue >= config.min && newValue <= config.max) {
      onChange({ ...params, [paramName]: newValue });
    }
  };

  return (
    <div className="space-y-4">
      {Object.entries(params).map(([paramName, config]) => (
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
            defaultValue={config.default}
            onChange={(e) => handleParamChange(paramName, e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
      ))}
    </div>
  );
};

export default StrategyParams; 