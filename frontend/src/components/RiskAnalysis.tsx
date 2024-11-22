'use client';

import React from 'react';
import type { BacktestResult } from '@/types';

interface Props {
  result: BacktestResult;
}

const RiskAnalysis: React.FC<Props> = ({ result }) => {
  // 计算风险指标
  const returns = result.equity_curve.map((point, i, arr) => 
    i === 0 ? 0 : (arr[i].value - arr[i-1].value) / arr[i-1].value
  );

  // 计算下行波动率
  const downside_returns = returns.filter(r => r < 0);
  const downside_risk = Math.sqrt(
    downside_returns.reduce((acc, r) => acc + r * r, 0) / downside_returns.length
  ) * Math.sqrt(252);

  // 计算索提诺比率
  const sortino_ratio = result.metrics.annual_return / downside_risk;

  // 计算VaR和CVaR
  const sorted_returns = [...returns].sort((a, b) => a - b);
  const var_95 = sorted_returns[Math.floor(returns.length * 0.05)];
  const var_99 = sorted_returns[Math.floor(returns.length * 0.01)];
  const cvar_95 = sorted_returns
    .slice(0, Math.floor(returns.length * 0.05))
    .reduce((acc, r) => acc + r, 0) / Math.floor(returns.length * 0.05);

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
        <h3 className="text-lg font-medium text-gray-900 mb-4">风险分析报告</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-700 mb-2">波动率分析</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>总波动率: {(result.metrics.volatility * 100).toFixed(2)}%</li>
              <li>下行波动率: {(downside_risk * 100).toFixed(2)}%</li>
              <li>最大回撤: {(result.metrics.max_drawdown * 100).toFixed(2)}%</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-700 mb-2">风险调整收益</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>夏普比率: {result.metrics.sharpe_ratio.toFixed(2)}</li>
              <li>索提诺比率: {sortino_ratio.toFixed(2)}</li>
              <li>信息比率: {((result.metrics.annual_return - 0.08) / result.metrics.volatility).toFixed(2)}</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-700 mb-2">风险价值(VaR)</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>95% VaR: {(var_95 * 100).toFixed(2)}%</li>
              <li>99% VaR: {(var_99 * 100).toFixed(2)}%</li>
              <li>95% CVaR: {(cvar_95 * 100).toFixed(2)}%</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-700 mb-2">交易风险</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>胜率: {(result.metrics.win_rate * 100).toFixed(2)}%</li>
              <li>盈亏比: {(Math.abs(returns.filter(r => r > 0).reduce((a, b) => a + b, 0) / 
                          returns.filter(r => r < 0).reduce((a, b) => a + b, 0))).toFixed(2)}</li>
              <li>最大连续亏损次数: {Math.max(...returns.reduce((acc, r) => {
                if (r < 0) acc[acc.length - 1]++;
                else if (acc[acc.length - 1] > 0) acc.push(0);
                return acc;
              }, [0]))}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskAnalysis; 