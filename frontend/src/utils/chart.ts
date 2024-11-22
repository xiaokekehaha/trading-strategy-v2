import { ChartData, StrategyMetrics } from '@/types';
import { IChartApi, createChart } from 'lightweight-charts';

export const createPortfolioChart = (
    container: HTMLElement,
    returns: ChartData[],
    drawdown: ChartData[]
): IChartApi => {
    const chart = createChart(container, {
        width: container.clientWidth,
        height: 400,
        layout: {
            background: { color: '#ffffff' },
            textColor: '#333',
        },
        grid: {
            vertLines: { color: '#f0f0f0' },
            horzLines: { color: '#f0f0f0' },
        },
        rightPriceScale: {
            scaleMargins: {
                top: 0.2,
                bottom: 0.2,
            },
        },
        timeScale: {
            timeVisible: true,
            secondsVisible: false,
        },
    });

    // 添加收益率曲线
    const returnsSeries = chart.addLineSeries({
        color: '#2196F3',
        lineWidth: 2,
        title: '累计收益',
    });
    returnsSeries.setData(returns);

    // 添加回撤曲线
    const drawdownSeries = chart.addLineSeries({
        color: '#FF5252',
        lineWidth: 1,
        title: '回撤',
    });
    drawdownSeries.setData(drawdown);

    // 添加图例
    const legend = document.createElement('div');
    legend.style.position = 'absolute';
    legend.style.left = '12px';
    legend.style.top = '12px';
    legend.style.zIndex = '1';
    legend.style.fontSize = '12px';
    legend.style.padding = '8px';
    legend.style.background = 'rgba(255, 255, 255, 0.8)';
    legend.style.borderRadius = '4px';
    container.appendChild(legend);

    const updateLegend = () => {
        legend.innerHTML = `
            <div style="color: #2196F3">累计收益</div>
            <div style="color: #FF5252">回撤</div>
        `;
    };
    updateLegend();

    return chart;
};

export const formatMetric = (value: number, precision: number = 2): string => {
  if (Math.abs(value) < 0.01) {
    return value.toExponential(precision);
  }
  return value.toFixed(precision);
}; 