'use client';

import React from 'react';
import type { BacktestResult } from '@/types';

interface Props {
  result: BacktestResult;
}

const StrategyOptimization: React.FC<Props> = ({ result }) => {
  const suggestions = [];
  
  // 收益率分析
  if (result.metrics.total_return < 0.1) {
    suggestions.push({
      aspect: '收益率',
      issue: '总收益率较低',
      suggestion: '考虑调整策略参数以提高收益率，或尝试其他技术指标组合'
    });
  }
  
  // 风险分析
  if (result.metrics.max_drawdown > 0.2) {
    suggestions.push({
      aspect: '风险控制',
      issue: '最大回撤过大',
      suggestion: '增加止损条件，优化仓位管理，或调整入场时机'
    });
  }
  
  // 交易频率分析
  const tradingDays = result.equity_curve.length;
  const tradesPerDay = result.metrics.total_trades / tradingDays;
  if (tradesPerDay > 0.5) {
    suggestions.push({
      aspect: '交易频率',
      issue: '交易频率过高',
      suggestion: '考虑增加信号过滤条件，减少假突破带来的交易'
    });
  }
  
  // 胜率分析
  if (result.metrics.win_rate < 0.4) {
    suggestions.push({
      aspect: '胜率',
      issue: '交易胜率偏低',
      suggestion: '优化入场条件，增加趋势确认指标，或调整止盈止损比例'
    });
  }
  
  // 夏普比率分析
  if (result.metrics.sharpe_ratio < 1) {
    suggestions.push({
      aspect: '风险收益比',
      issue: '风险调整后收益不理想',
      suggestion: '优化策略以提高单位风险收益，考虑增加风险控制措施'
    });
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
      <h3 className="text-lg font-medium text-gray-900 mb-4">策略优化建议</h3>
      
      {suggestions.length > 0 ? (
        <div className="space-y-4">
          {suggestions.map((item, index) => (
            <div key={index} className="p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center mb-2">
                <span className="font-medium text-blue-700">{item.aspect}</span>
                <span className="mx-2 text-gray-400">|</span>
                <span className="text-red-600">{item.issue}</span>
              </div>
              <p className="text-sm text-gray-600">{item.suggestion}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-green-600">
          策略表现良好，暂无需要优化的重要问题。
        </p>
      )}
    </div>
  );
};

export default StrategyOptimization; 