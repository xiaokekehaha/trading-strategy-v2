'use client';

import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartData,
  ChartOptions,
  ScriptableContext
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface Props {
  returns: number[];
  drawdown: number[];
  positions: number[];
  dates: string[];
  trades?: Array<{
    date: string;
    type: 'buy' | 'sell';
    price: number;
  }>;
  stockData: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
}

const BacktestChart: React.FC<Props> = ({ 
  returns = [], 
  drawdown = [], 
  positions = [], 
  dates = [], 
  trades = [],
  stockData = [] 
}) => {
  const options: ChartOptions<'line'> = {
    responsive: true,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
        align: 'start',
        labels: {
          boxWidth: 16,
          boxHeight: 16,
          padding: 20,
          color: '#E5E7EB',
          font: { size: 12 },
          usePointStyle: true,
          pointStyle: 'circle'
        }
      },
      title: {
        display: true,
        text: '回测结果图表',
        color: '#E5E7EB',
        font: {
          size: 16,
          weight: 'bold'
        },
        padding: { bottom: 30 }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(17, 24, 39, 0.8)',
        titleFont: { size: 12 },
        bodyFont: { size: 12 },
        padding: 12,
        callbacks: {
          label: function(context) {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            
            if (context.dataset.yAxisID === 'price') {
              return `${label}: ${value.toFixed(2)}`;
            }
            return `${label}: ${(value * 100).toFixed(2)}%`;
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          color: '#374151',
        },
        ticks: {
          color: '#9CA3AF',
          font: { size: 11 },
          maxRotation: 0
        }
      },
      price: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        grid: {
          color: '#374151',
        },
        ticks: {
          color: '#9CA3AF',
          font: { size: 11 }
        },
        title: {
          display: true,
          text: '价格',
          color: '#9CA3AF',
        }
      },
      percent: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        grid: {
          drawOnChartArea: false,
        },
        ticks: {
          color: '#9CA3AF',
          font: { size: 11 },
          callback: (value) => `${(value * 100).toFixed(1)}%`
        }
      },
    },
  };

  const chartData: ChartData<'line'> = {
    labels: dates,
    datasets: [
      // 股票价格
      {
        type: 'line',
        label: '股票价格',
        data: stockData?.map(d => d.close) ?? [],
        borderColor: 'rgb(156, 163, 175)',
        backgroundColor: 'rgba(156, 163, 175, 0.1)',
        yAxisID: 'price',
        tension: 0.1,
        fill: false,
        borderWidth: 1,
        pointRadius: 0,
      },
      // 买入点
      {
        type: 'scatter',
        label: '买入信号',
        data: trades?.filter(t => t.type === 'buy').map(t => ({
          x: t.date,
          y: t.price
        })) ?? [],
        pointStyle: 'triangle',
        pointRadius: 8,
        pointHoverRadius: 12,
        backgroundColor: 'rgb(34, 197, 94)',
        borderColor: '#fff',
        borderWidth: 2,
        yAxisID: 'price',
      },
      // 卖出点
      {
        type: 'scatter',
        label: '卖出信号',
        data: trades?.filter(t => t.type === 'sell').map(t => ({
          x: t.date,
          y: t.price
        })) ?? [],
        pointStyle: 'triangle',
        rotation: 180,
        pointRadius: 8,
        pointHoverRadius: 12,
        backgroundColor: 'rgb(239, 68, 68)',
        borderColor: '#fff',
        borderWidth: 2,
        yAxisID: 'price',
      },
      // 策略收益
      {
        type: 'line',
        label: '策略收益',
        data: returns?.map(r => r - 1) ?? [],
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        yAxisID: 'percent',
        tension: 0.1,
        fill: true,
        borderWidth: 1.5,
        pointRadius: 0,
      },
      // 回撤
      {
        type: 'line',
        label: '回撤',
        data: drawdown ?? [],
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        yAxisID: 'percent',
        tension: 0.1,
        fill: true,
        borderWidth: 1.5,
        pointRadius: 0
      },
    ],
  };

  if (!dates.length || !stockData?.length) {
    return (
      <div className="bg-[#1E293B] rounded-lg p-6 shadow-lg border border-gray-700 flex items-center justify-center h-[400px]">
        <p className="text-gray-400">暂无数据</p>
      </div>
    );
  }

  return (
    <div className="bg-[#1E293B] rounded-lg p-6 shadow-lg border border-gray-700">
      <div className="text-right text-sm text-gray-400 mb-4">
        总收益: {(((returns?.[returns.length - 1] ?? 0) - 1) * 100).toFixed(2)}% | 
        最大回撤: {((Math.min(...(drawdown ?? [0]))) * 100).toFixed(2)}%
      </div>
      <Line options={options} data={chartData} />
    </div>
  );
};

export default BacktestChart; 