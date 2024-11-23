'use client';

import React, { useState } from 'react';
import { Settings, Moon, Sun, Layout, Eye } from 'lucide-react';
import { useTheme } from './ThemeProvider';

interface ChartConfig {
  showVolume: boolean;
  showGrid: boolean;
  showTooltip: boolean;
  showCrosshair: boolean;
  chartType: 'candles' | 'line' | 'area';
  timeframe: '1D' | '1W' | '1M' | '3M' | '6M' | '1Y' | 'ALL';
}

interface Props {
  config: ChartConfig;
  onConfigChange: (config: ChartConfig) => void;
}

const ChartSettings: React.FC<Props> = ({ config, onConfigChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const { theme, toggleTheme } = useTheme();

  const handleChange = (key: keyof ChartConfig, value: any) => {
    onConfigChange({
      ...config,
      [key]: value
    });
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
      >
        <Settings className="w-5 h-5 text-gray-600 dark:text-gray-300" />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 z-50">
          <div className="space-y-4">
            {/* 主题切换 */}
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-300">主题</span>
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                {theme === 'light' ? (
                  <Moon className="w-5 h-5" />
                ) : (
                  <Sun className="w-5 h-5" />
                )}
              </button>
            </div>

            {/* 图表类型 */}
            <div className="space-y-2">
              <span className="text-sm text-gray-600 dark:text-gray-300">图表类型</span>
              <div className="grid grid-cols-3 gap-2">
                {['candles', 'line', 'area'].map(type => (
                  <button
                    key={type}
                    onClick={() => handleChange('chartType', type)}
                    className={`px-3 py-1.5 text-sm rounded-lg ${
                      config.chartType === type
                        ? 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    {type === 'candles' ? 'K线' : type === 'line' ? '折线' : '面积'}
                  </button>
                ))}
              </div>
            </div>

            {/* 显示选项 */}
            <div className="space-y-2">
              <span className="text-sm text-gray-600 dark:text-gray-300">显示选项</span>
              <div className="space-y-2">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={config.showVolume}
                    onChange={e => handleChange('showVolume', e.target.checked)}
                    className="rounded text-blue-600"
                  />
                  <span className="text-sm">显示成交量</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={config.showGrid}
                    onChange={e => handleChange('showGrid', e.target.checked)}
                    className="rounded text-blue-600"
                  />
                  <span className="text-sm">显示网格</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={config.showTooltip}
                    onChange={e => handleChange('showTooltip', e.target.checked)}
                    className="rounded text-blue-600"
                  />
                  <span className="text-sm">显示提示</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={config.showCrosshair}
                    onChange={e => handleChange('showCrosshair', e.target.checked)}
                    className="rounded text-blue-600"
                  />
                  <span className="text-sm">显示十字光标</span>
                </label>
              </div>
            </div>

            {/* 时间周期 */}
            <div className="space-y-2">
              <span className="text-sm text-gray-600 dark:text-gray-300">时间周期</span>
              <div className="grid grid-cols-4 gap-2">
                {['1D', '1W', '1M', '3M', '6M', '1Y', 'ALL'].map(tf => (
                  <button
                    key={tf}
                    onClick={() => handleChange('timeframe', tf)}
                    className={`px-2 py-1 text-sm rounded-lg ${
                      config.timeframe === tf
                        ? 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    {tf}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChartSettings; 