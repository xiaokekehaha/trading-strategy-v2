import React, { useEffect, useRef } from 'react';
import { createChart, IChartApi } from 'lightweight-charts';

interface TimeSeriesData {
  time: string;
  value: number;
}

interface IndicatorChartProps {
  data: TimeSeriesData[];
  type: 'MA' | 'MACD' | 'RSI' | 'BOLL';
  width?: number;
  height?: number;
}

export const IndicatorChart: React.FC<IndicatorChartProps> = ({
  data,
  type,
  width = 800,
  height = 200
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (chartContainerRef.current) {
      const chart = createChart(chartContainerRef.current, {
        width,
        height,
        layout: {
          background: { color: '#ffffff' },
          textColor: '#333',
        },
        grid: {
          vertLines: { color: '#f0f0f0' },
          horzLines: { color: '#f0f0f0' },
        },
        rightPriceScale: {
          scaleMargins: {
            top: 0.1,
            bottom: 0.1,
          },
        },
        timeScale: {
          timeVisible: true,
          secondsVisible: false,
        },
      });

      const series = chart.addLineSeries({
        color: getIndicatorColor(type),
        lineWidth: 2,
        title: type,
      });

      series.setData(data);
      chartRef.current = chart;

      return () => {
        chart.remove();
      };
    }
  }, [data, type, width, height]);

  return <div ref={chartContainerRef} />;
};

const getIndicatorColor = (type: string): string => {
  switch (type) {
    case 'MA':
      return '#2196F3';
    case 'MACD':
      return '#FF9800';
    case 'RSI':
      return '#4CAF50';
    case 'BOLL':
      return '#9C27B0';
    default:
      return '#000000';
  }
}; 