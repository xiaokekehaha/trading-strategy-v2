'use client';

import React, { useState } from 'react';
import { TECHNICAL_INDICATORS } from '@/lib/constants';

interface Props {
  selectedIndicators: string[];
  onIndicatorChange: (indicators: string[]) => void;
}

interface IndicatorParams {
  [key: string]: {
    period?: number;
    shortPeriod?: number;
    longPeriod?: number;
    signalPeriod?: number;
    standardDeviations?: number;
    overbought?: number;
    oversold?: number;
  };
}

const IndicatorSelector: React.FC<Props> = ({
  selectedIndicators,
  onIndicatorChange,
}) => {
  const [showParams, setShowParams] = useState(false);
  const [params, setParams] = useState<IndicatorParams>({});

  const handleIndicatorToggle = (indicatorId: string) => {
    if (selectedIndicators.includes(indicatorId)) {
      onIndicatorChange(selectedIndicators.filter(id => id !== indicatorId));
    } else {
      // 添加指标时设置默认参数
      setParams(prev => ({
        ...prev,
        [indicatorId]: getDefaultParams(indicatorId),
      }));
      onIndicatorChange([...selectedIndicators, indicatorId]);
    }
  };

  const getDefaultParams = (indicatorId: string) => {
    switch (indicatorId) {
      case 'VOL':
        return { period: 20 };
      case 'VOLR':
        return { period: 5 };
      case 'KDJ':
        return { period: 14, overbought: 80, oversold: 20 };
      case 'MACD':
        return { shortPeriod: 12, longPeriod: 26, signalPeriod: 9 };
      case 'RSI':
        return { period: 14, overbought: 70, oversold: 30 };
      default:
        return {};
    }
  };

  const handleParamChange = (indicatorId: string, paramName: string, value: number) => {
    setParams(prev => ({
      ...prev,
      [indicatorId]: {
        ...prev[indicatorId],
        [paramName]: value,
      },
    }));
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {TECHNICAL_INDICATORS.map(indicator => (
          <button
            key={indicator.id}
            onClick={() => handleIndicatorToggle(indicator.id)}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              selectedIndicators.includes(indicator.id)
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700'
            }`}
          >
            {indicator.name}
          </button>
        ))}
      </div>

      {selectedIndicators.length > 0 && (
        <div className="mt-4">
          <button
            onClick={() => setShowParams(!showParams)}
            className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
          >
            {showParams ? '隐藏参数设置' : '显示参数设置'}
          </button>

          {showParams && (
            <div className="mt-2 space-y-4">
              {selectedIndicators.map(indicatorId => (
                <div key={indicatorId} className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <h4 className="font-medium mb-2">
                    {TECHNICAL_INDICATORS.find(i => i.id === indicatorId)?.name}
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    {Object.entries(params[indicatorId] || {}).map(([paramName, value]) => (
                      <div key={paramName}>
                        <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                          {getParamLabel(paramName)}
                        </label>
                        <input
                          type="number"
                          value={value}
                          onChange={(e) => handleParamChange(
                            indicatorId,
                            paramName,
                            parseFloat(e.target.value)
                          )}
                          className="w-full px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const getParamLabel = (paramName: string): string => {
  switch (paramName) {
    case 'period':
      return '周期';
    case 'shortPeriod':
      return '短周期';
    case 'longPeriod':
      return '长周期';
    case 'signalPeriod':
      return '信号周期';
    case 'standardDeviations':
      return '标准差倍数';
    case 'overbought':
      return '超买值';
    case 'oversold':
      return '超卖值';
    default:
      return paramName;
  }
};

export default IndicatorSelector; 