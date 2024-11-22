'use client';

import React, { useEffect, useRef } from 'react';
import { createChart, CrosshairMode, IChartApi, CandlestickData } from 'lightweight-charts';
import type { BacktestResult } from '@/types';

interface Props {
  result: BacktestResult;
}

const BacktestChartComponent: React.FC<Props> = ({ result }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const container = chartContainerRef.current;
    const chart = createChart(container, {
      width: container.clientWidth,
      height: 600,
      layout: {
        background: { color: '#ffffff' },
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      rightPriceScale: {
        borderVisible: false,
        scaleMargins: {
          top: 0.1,
          bottom: 0.2,
        },
      },
      timeScale: {
        borderVisible: false,
        timeVisible: true,
        secondsVisible: false,
      },
      crosshair: {
        mode: CrosshairMode.Normal,
      },
    });

    // 添加K线图
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });

    // 设置K线数据
    const candleData: CandlestickData[] = result.price_data.map(p => ({
      time: p.time,
      open: p.open,
      high: p.high,
      low: p.low,
      close: p.close,
    }));
    candlestickSeries.setData(candleData);

    // 添加成交量图
    const volumeSeries = chart.addHistogramSeries({
      color: '#26a69a',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: 'volume',
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });

    // 设置成交量数据
    const volumeData = result.price_data.map(p => ({
      time: p.time,
      value: p.volume,
      color: p.close >= p.open ? '#26a69a' : '#ef5350',
    }));
    volumeSeries.setData(volumeData);

    // 添加交易标记
    const markers = result.trades.map(trade => ({
      time: trade.time.split(' ')[0],
      position: trade.type === 'buy' ? 'belowBar' : 'aboveBar',
      color: trade.type === 'buy' ? '#2196F3' : '#FF5252',
      shape: trade.type === 'buy' ? 'arrowUp' : 'arrowDown',
      text: `${trade.type === 'buy' ? '买入' : '卖出'} ¥${trade.price.toFixed(2)}${
        trade.profit !== null ? ` (${trade.profit > 0 ? '+' : ''}${trade.profit.toFixed(2)})` : ''
      }`,
    }));
    candlestickSeries.setMarkers(markers);

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
    legend.innerHTML = `
      <div style="margin-bottom: 4px">
        <span style="color: #26a69a">●</span> 上涨
        <span style="color: #ef5350; margin-left: 12px">●</span> 下跌
      </div>
      <div>
        <span style="color: #2196F3">▲</span> 买入
        <span style="color: #FF5252; margin-left: 12px">▼</span> 卖出
      </div>
    `;
    container.appendChild(legend);

    // 自适应大小
    const handleResize = () => {
      chart.applyOptions({
        width: container.clientWidth,
      });
    };

    window.addEventListener('resize', handleResize);
    chart.timeScale().fitContent();

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
      container.removeChild(legend);
    };
  }, [result]);

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-gray-900">回测结果图表</h3>
        <div className="text-sm text-gray-500">
          总收益: {(result.metrics.total_return * 100).toFixed(2)}%
          {' | '}
          最大回撤: {(result.metrics.max_drawdown * 100).toFixed(2)}%
        </div>
      </div>
      <div className="relative" style={{ height: '600px' }}>
        <div ref={chartContainerRef} style={{ position: 'absolute', width: '100%', height: '100%' }} />
      </div>
    </div>
  );
};

export default BacktestChartComponent; 