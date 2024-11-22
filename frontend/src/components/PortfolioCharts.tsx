import React, { useEffect, useRef } from 'react';
import { createChart, IChartApi } from 'lightweight-charts';

interface ChartData {
    time: string;
    value: number;
}

interface PortfolioChartsProps {
    returns: ChartData[];
    drawdown: ChartData[];
    metrics: {
        total_return: number;
        annual_return: number;
        sharpe_ratio: number;
        max_drawdown: number;
        win_rate: number;
    };
}

export const PortfolioCharts: React.FC<PortfolioChartsProps> = ({
    returns,
    drawdown,
    metrics
}) => {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);

    useEffect(() => {
        if (chartContainerRef.current) {
            // 创建图表
            const chart = createChart(chartContainerRef.current, {
                width: 800,
                height: 400,
                layout: {
                    background: { color: '#ffffff' },
                    textColor: '#333',
                },
                grid: {
                    vertLines: { color: '#f0f0f0' },
                    horzLines: { color: '#f0f0f0' },
                },
            });

            // 添加收益率曲线
            const returnsSeries = chart.addLineSeries({
                color: '#2196F3',
                lineWidth: 2,
            });
            returnsSeries.setData(returns);

            // 添加回撤曲线
            const drawdownSeries = chart.addLineSeries({
                color: '#FF5252',
                lineWidth: 1,
            });
            drawdownSeries.setData(drawdown);

            chartRef.current = chart;

            // 清理函数
            return () => {
                chart.remove();
            };
        }
    }, [returns, drawdown]);

    return (
        <div className="w-full p-4">
            <div className="mb-4 grid grid-cols-5 gap-4">
                <MetricCard
                    title="总收益"
                    value={`${(metrics.total_return * 100).toFixed(2)}%`}
                />
                <MetricCard
                    title="年化收益"
                    value={`${(metrics.annual_return * 100).toFixed(2)}%`}
                />
                <MetricCard
                    title="夏普比率"
                    value={metrics.sharpe_ratio.toFixed(2)}
                />
                <MetricCard
                    title="最大回撤"
                    value={`${(metrics.max_drawdown * 100).toFixed(2)}%`}
                />
                <MetricCard
                    title="胜率"
                    value={`${(metrics.win_rate * 100).toFixed(2)}%`}
                />
            </div>
            <div ref={chartContainerRef} className="w-full h-[400px]" />
        </div>
    );
};

interface MetricCardProps {
    title: string;
    value: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value }) => (
    <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-sm text-gray-500">{title}</h3>
        <p className="text-xl font-semibold">{value}</p>
    </div>
); 