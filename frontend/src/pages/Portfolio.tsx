import React, { useState } from 'react';
import { useQuery, useMutation } from 'react-query';
import { PortfolioCharts } from '../components/PortfolioCharts';
import { OptimizationForm } from '../components/OptimizationForm';
import { getStrategies, optimizePortfolio } from '../services/api';
import type { PortfolioResult, Strategy } from '../types';

export const Portfolio: React.FC = () => {
    const [result, setResult] = useState<PortfolioResult | null>(null);

    const { data: strategies = [] } = useQuery<Strategy[]>('strategies', getStrategies);

    const { mutate: optimize, isLoading } = useMutation<PortfolioResult>(optimizePortfolio, {
        onSuccess: (data: PortfolioResult) => {
            setResult(data);
        },
    });

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold mb-8">投资组合优化</h1>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div>
                    <OptimizationForm
                        onSubmit={optimize}
                        availableStrategies={strategies.map((s: Strategy) => s.name)}
                    />
                </div>
                
                <div>
                    {isLoading && (
                        <div className="flex items-center justify-center h-full">
                            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500" />
                        </div>
                    )}
                    
                    {result && (
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
                    )}
                </div>
            </div>
        </div>
    );
}; 