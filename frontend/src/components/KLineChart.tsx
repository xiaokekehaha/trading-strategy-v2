'use client';

import React, { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, ColorType, CrosshairMode } from 'lightweight-charts';
import { TIMEFRAMES } from '@/lib/constants';

interface KLineData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface ChartConfig {
  showVolume: boolean;
  showGrid: boolean;
  showTooltip: boolean;
  showCrosshair: boolean;
  chartType: 'candles' | 'line' | 'area';
}

interface Props {
  data: KLineData[];
  timeframe: string;
  onTimeframeChange: (timeframe: string) => void;
  chartConfig: ChartConfig;
}

const KLineChart: React.FC<Props> = ({
  data,
  timeframe,
  onTimeframeChange,
  chartConfig
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    if (!chartContainerRef.current || !chartConfig) return;

    // 图表配置
    const chartOptions = {
      layout: {
        background: { color: isDarkMode ? '#141B2D' : '#ffffff' },
        textColor: isDarkMode ? '#d1d4dc' : '#000000',
      },
      grid: {
        vertLines: { 
          visible: chartConfig.showGrid,
          color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
        },
        horzLines: { 
          visible: chartConfig.showGrid,
          color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
        },
      },
      crosshair: {
        mode: chartConfig.showCrosshair ? CrosshairMode.Normal : CrosshairMode.Magnet,
        vertLine: {
          width: 1,
          color: isDarkMode ? '#758696' : '#9598a1',
          style: 1,
        },
        horzLine: {
          width: 1,
          color: isDarkMode ? '#758696' : '#9598a1',
          style: 1,
        },
      },
      timeScale: {
        borderColor: isDarkMode ? '#363c4e' : '#2b2b43',
        timeVisible: true,
        secondsVisible: false,
      },
      rightPriceScale: {
        borderColor: isDarkMode ? '#363c4e' : '#2b2b43',
      },
    };

    // 创建图表
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 600,
      ...chartOptions,
    });

    // 根据配置创建主图表
    const mainSeries = chartConfig.chartType === 'candles' 
      ? chart.addCandlestickSeries({
          upColor: '#26a69a',
          downColor: '#ef5350',
          borderVisible: false,
          wickUpColor: '#26a69a',
          wickDownColor: '#ef5350',
        })
      : chartConfig.chartType === 'line'
      ? chart.addLineSeries({
          color: '#2962FF',
          lineWidth: 2,
        })
      : chart.addAreaSeries({
          topColor: 'rgba(41, 98, 255, 0.3)',
          bottomColor: 'rgba(41, 98, 255, 0)',
          lineColor: '#2962FF',
          lineWidth: 2,
        });

    // 添加成交量图表
    if (chartConfig.showVolume) {
      const volumeSeries = chart.addHistogramSeries({
        color: '#26a69a',
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: '', // 在主图表下方显示
      });

      volumeSeries.setData(
        data.map(d => ({
          time: d.time,
          value: d.volume,
          color: d.close >= d.open ? '#26a69a' : '#ef5350',
        }))
      );
    }

    // 设置主图表数据
    mainSeries.setData(data);

    // 响应式调整
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);
    chartRef.current = chart;

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
      }
    };
  }, [data, chartConfig, isDarkMode]);

  return (
    <div className="space-y-4">
      {/* 时间周期选择器 */}
      <div className="flex space-x-2">
        {TIMEFRAMES.map(tf => (
          <button
            key={tf.id}
            onClick={() => onTimeframeChange(tf.id)}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              timeframe === tf.id
                ? 'bg-blue-600 text-white'
                : 'hover:bg-gray-100 dark:hover:bg-gray-800'
            }`}
          >
            {tf.name}
          </button>
        ))}
      </div>

      {/* 图表容器 */}
      <div 
        ref={chartContainerRef} 
        className="w-full bg-white dark:bg-dark-lighter rounded-lg shadow-lg"
      />
    </div>
  );
};

export default KLineChart; 