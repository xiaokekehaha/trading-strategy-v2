import React, { useEffect, useRef } from 'react';
import { createChart, IChartApi } from 'lightweight-charts';

interface TimeSeriesData {
  time: string;
  value: number;
}

interface PerformanceChartProps {
  returns: TimeSeriesData[];
  drawdown: TimeSeriesData[];
  width?: number;
  height?: number;
}

export const PerformanceChart: React.FC<PerformanceChartProps> = ({
  returns,
  drawdown,
  width = 800,
  height = 400
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
            top: 0.2,
            bottom: 0.2,
          },
        },
        timeScale: {
          timeVisible: true,
          secondsVisible: false,
        },
      });

      // 添加收益率曲线
      const returnsSeries = chart.addLineSeries({
        color: '#2196F3',
        lineWidth: 2,
        title: '累计收益',
      });
      returnsSeries.setData(returns);

      // 添加回撤曲线
      const drawdownSeries = chart.addLineSeries({
        color: '#FF5252',
        lineWidth: 1,
        title: '回撤',
        priceScaleId: 'right',
      });
      drawdownSeries.setData(drawdown);

      // 添加图例
      const legend = document.createElement('div');
      legend.style.position = 'absolute';
      legend.style.left = '12px';
      legend.style.top = '12px';
      legend.style.zIndex = '1';
      legend.style.fontSize = '12px';
      legend.style.padding = '8px';
      legend.style.background = 'rgba(255, 255, 255, 0.8)';
      legend.style.borderRadius = '4px';
      chartContainerRef.current.appendChild(legend);

      const updateLegend = () => {
        const lastReturn = returns[returns.length - 1]?.value || 0;
        const lastDrawdown = drawdown[drawdown.length - 1]?.value || 0;
        legend.innerHTML = `
          <div style="color: #2196F3">累计收益: ${(lastReturn * 100).toFixed(2)}%</div>
          <div style="color: #FF5252">当前回撤: ${(lastDrawdown * 100).toFixed(2)}%</div>
        `;
      };
      updateLegend();

      chartRef.current = chart;

      return () => {
        chart.remove();
      };
    }
  }, [returns, drawdown, width, height]);

  return <div ref={chartContainerRef} className="relative" />;
}; 