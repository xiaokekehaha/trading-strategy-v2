'use client';

import React from 'react';
import { TradeRecord } from '@/types/backtest';
import { formatDate, formatMoney, formatPercentage } from '@/lib/utils';

interface Props {
  trades: TradeRecord[];
  metrics?: {
    total_return: number;
    max_drawdown: number;
  };
}

const TradesTable: React.FC<Props> = ({ trades, metrics }) => {
  return (
    <div className="bg-[#1E293B] rounded-lg p-6 shadow-lg border border-gray-700">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-200 mb-2">
          交易记录 ({trades.length}笔)
        </h3>
        {metrics && (
          <div className="text-sm text-gray-400">
            总收益率: {formatPercentage(metrics.total_return)} | 
            最大回撤: {formatPercentage(metrics.max_drawdown)}
          </div>
        )}
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                日期
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                类型
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                价格
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                数量
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                收益
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {trades.map((trade, index) => (
              <tr key={index}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatDate(trade.date)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    trade.type === 'buy' 
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {trade.type === 'buy' ? '买入' : '卖出'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatMoney(trade.price)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {trade.shares.toFixed(2)}
                </td>
                <td className={`px-6 py-4 whitespace-nowrap text-sm ${
                  trade.profit > 0 
                    ? 'text-green-600' 
                    : trade.profit < 0 
                    ? 'text-red-600' 
                    : 'text-gray-900'
                }`}>
                  {trade.profit > 0 ? '+' : ''}{formatMoney(trade.profit)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TradesTable; 