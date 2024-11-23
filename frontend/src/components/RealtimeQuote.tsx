'use client';

import React from 'react';
import { useMarketData } from '@/hooks/useMarketData';
import { formatMoney, formatNumber, formatPercentage } from '@/lib/utils';

interface Props {
  symbol: string;
}

const RealtimeQuote: React.FC<Props> = ({ symbol }) => {
  const { data, isConnected, error } = useMarketData(symbol);

  if (error) {
    return (
      <div className="bg-red-50 p-4 rounded-lg">
        <p className="text-red-600">数据加载失败: {error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-gray-50 p-4 rounded-lg animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-24 mb-2"></div>
        <div className="h-8 bg-gray-200 rounded w-32"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h2 className="text-2xl font-bold">{symbol}</h2>
          <p className="text-sm text-gray-500">
            最后更新: {new Date(data.lastUpdate).toLocaleTimeString()}
          </p>
        </div>
        <div className={`text-right ${isConnected ? 'text-green-500' : 'text-gray-400'}`}>
          {isConnected ? '实时' : '断开'}
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <div className="text-sm text-gray-500">当前价格</div>
          <div className={`text-2xl font-bold ${data.priceChangeClass}`}>
            {formatMoney(data.price)}
          </div>
        </div>

        <div>
          <div className="text-sm text-gray-500">涨跌幅</div>
          <div className={`text-xl font-semibold ${
            data.changePercent > 0 ? 'text-green-600' : 
            data.changePercent < 0 ? 'text-red-600' : 'text-gray-600'
          }`}>
            {formatPercentage(data.changePercent)}
          </div>
        </div>

        <div>
          <div className="text-sm text-gray-500">涨跌额</div>
          <div className={`text-xl font-semibold ${
            data.change > 0 ? 'text-green-600' : 
            data.change < 0 ? 'text-red-600' : 'text-gray-600'
          }`}>
            {formatMoney(data.change)}
          </div>
        </div>

        <div>
          <div className="text-sm text-gray-500">成交量</div>
          <div className="text-xl font-semibold text-gray-900">
            {formatNumber(data.volume)}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealtimeQuote; 