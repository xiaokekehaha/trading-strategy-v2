import React from 'react';
import { BacktestResult } from '@/types';
import { PortfolioCharts } from './PortfolioCharts';
import { StrategyMetrics } from './StrategyMetrics';
import DeepLearningMetrics from './DeepLearningMetrics';

interface BacktestResultsProps {
    result: BacktestResult;
    strategyName: string;
}

export const BacktestResults: React.FC<BacktestResultsProps> = ({
    result,
    strategyName
}) => {
    const isDeepLearning = ['mlp', 'lstm_mlp', 'cnn_mlp'].includes(strategyName);

    return (
        <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-2xl font-bold mb-6">
                    {strategyName} 回测结果
                </h2>
                
                <PortfolioCharts
                    returns={result.returns}
                    drawdown={result.drawdown}
                    metrics={{
                        total_return: result.total_return,
                        annual_return: result.annual_return,
                        sharpe_ratio: result.sharpe_ratio,
                        max_drawdown: result.max_drawdown,
                        win_rate: result.win_rate
                    }}
                />
            </div>
            
            <StrategyMetrics metrics={result} />
            
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">交易统计</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <StatCard
                        title="总交易次数"
                        value={result.returns.length.toString()}
                    />
                    <StatCard
                        title="平均持仓时间"
                        value={`${Math.round(result.returns.length / 2)} 天`}
                    />
                    <StatCard
                        title="盈利交易"
                        value={`${Math.round(result.win_rate * 100)}%`}
                    />
                    <StatCard
                        title="亏损交易"
                        value={`${Math.round((1 - result.win_rate) * 100)}%`}
                    />
                </div>
            </div>
            
            {isDeepLearning && result.training_history && (
                <DeepLearningMetrics trainingHistory={result.training_history} />
            )}
        </div>
    );
};

interface StatCardProps {
    title: string;
    value: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value }) => {
    return (
        <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="text-sm text-gray-500">{title}</h4>
            <p className="text-xl font-semibold text-gray-900">{value}</p>
        </div>
    );
}; 