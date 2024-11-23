'use client';

import React from 'react';
import { formatMoney, formatNumber, formatPercentage } from '@/lib/utils';

interface ExtendedMarketDataProps {
  data: {
    weekHigh52: number;
    avgPrice: number;
    peRatio: number;
    dividendYield: number;
    shortRatio: number;
    floatShares: number;
  };
}

const ExtendedMarketData: React.FC<ExtendedMarketDataProps> = ({ data }) => {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium text-gray-900 mb-4">扩展数据</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <DataItem 
          label="52周最高价" 
          value={formatMoney(data.weekHigh52)}
          tooltip="过去52周内的最高交易价格"
        />
        <DataItem 
          label="平均价格" 
          value={formatMoney(data.avgPrice)}
          tooltip="当日交易量加权平均价格"
        />
        <DataItem 
          label="市盈率(TTM)" 
          value={data.peRatio.toFixed(2)}
          tooltip="股价与每股收益的比率(滚动12个月)"
        />
        <DataItem 
          label="股息率(TTM)" 
          value={formatPercentage(data.dividendYield)}
          tooltip="年度股息与当前股价的比率(滚动12个月)"
        />
        <DataItem 
          label="空头比率" 
          value={data.shortRatio.toFixed(2)}
          tooltip="空头持仓量与日均交易量的比率"
        />
        <DataItem 
          label="流通股数" 
          value={formatNumber(data.floatShares)}
          tooltip="实际可在市场上交易的股票数量"
        />
      </div>
    </div>
  );
};

interface DataItemProps {
  label: string;
  value: string;
  tooltip?: string;
}

const DataItem: React.FC<DataItemProps> = ({ label, value, tooltip }) => {
  return (
    <div className="p-3 rounded-lg bg-gray-50 group relative">
      <div className="text-sm text-gray-500 mb-1 flex items-center">
        {label}
        {tooltip && (
          <div className="hidden group-hover:block absolute bottom-full left-1/2 transform -translate-x-1/2 w-48 p-2 bg-gray-900 text-white text-xs rounded shadow-lg z-10">
            {tooltip}
          </div>
        )}
      </div>
      <div className="text-lg font-semibold text-gray-900">
        {value}
      </div>
    </div>
  );
};

export default ExtendedMarketData; 