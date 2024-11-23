'use client';

import React from 'react';
import { formatMoney, formatNumber, formatPercentage } from '@/lib/utils';

interface MarketDataProps {
  data: {
    open: number;
    close: number;
    high: number;
    low: number;
    volume: number;
    marketCap: number;
    change: number;
    changePercent: number;
  };
}

const MarketData: React.FC<MarketDataProps> = ({ data }) => {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium text-gray-900 mb-4">基础行情</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <DataItem 
          label="开盘价" 
          value={formatMoney(data.open)} 
        />
        <DataItem 
          label="收盘价" 
          value={formatMoney(data.close)}
          highlight={true}
        />
        <DataItem 
          label="最高价" 
          value={formatMoney(data.high)}
          trend="up"
        />
        <DataItem 
          label="最低价" 
          value={formatMoney(data.low)}
          trend="down"
        />
        <DataItem 
          label="成交量" 
          value={formatNumber(data.volume)}
        />
        <DataItem 
          label="市值" 
          value={formatMoney(data.marketCap)}
        />
        <DataItem 
          label="涨跌额" 
          value={formatMoney(data.change)}
          trend={data.change >= 0 ? 'up' : 'down'}
        />
        <DataItem 
          label="涨跌幅" 
          value={formatPercentage(data.changePercent)}
          trend={data.changePercent >= 0 ? 'up' : 'down'}
        />
      </div>
    </div>
  );
};

interface DataItemProps {
  label: string;
  value: string;
  highlight?: boolean;
  trend?: 'up' | 'down';
}

const DataItem: React.FC<DataItemProps> = ({ 
  label, 
  value, 
  highlight = false,
  trend 
}) => {
  return (
    <div className="p-3 rounded-lg bg-gray-50">
      <div className="text-sm text-gray-500 mb-1">{label}</div>
      <div className={`text-lg font-semibold ${
        trend === 'up' ? 'text-green-600' :
        trend === 'down' ? 'text-red-600' :
        highlight ? 'text-blue-600' : 'text-gray-900'
      }`}>
        {value}
        {trend && (
          <span className="ml-1">
            {trend === 'up' ? '↑' : '↓'}
          </span>
        )}
      </div>
    </div>
  );
};

export default MarketData; 