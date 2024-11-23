'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { ThemeProvider } from '@/components/ThemeProvider';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import StockList from '@/components/layout/StockList';
import Navbar from '@/components/layout/Navbar';
import KLineChart from '@/components/KLineChart';
import MarketData from '@/components/MarketData';
import ExtendedMarketData from '@/components/ExtendedMarketData';
import IndicatorSelector from '@/components/IndicatorSelector';
import ChartSettings from '@/components/ChartSettings';
import { useMarketData } from '@/hooks/useMarketData';
import { ChartConfig } from '@/types/chart';
import { BarChart2, LineChart } from 'lucide-react';

const queryClient = new QueryClient();

export default function Home() {
  const router = useRouter();
  const [selectedStock, setSelectedStock] = React.useState<string>('AAPL');
  const [chartConfig, setChartConfig] = React.useState<ChartConfig>({
    showVolume: true,
    showGrid: true,
    showTooltip: true,
    showCrosshair: true,
    chartType: 'candles',
    timeframe: '1D'
  });

  const { 
    quote, 
    isLoadingQuote, 
    quoteError,
    getKLineData 
  } = useMarketData(selectedStock);

  const [klineData, setKlineData] = React.useState([]);

  // 加载K线数据
  React.useEffect(() => {
    const loadKlineData = async () => {
      try {
        const data = await getKLineData(chartConfig.timeframe);
        setKlineData(data);
      } catch (error) {
        console.error('加载K线数据失败:', error);
      }
    };

    if (selectedStock) {
      loadKlineData();
    }
  }, [selectedStock, chartConfig.timeframe, getKLineData]);

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <div className="min-h-screen bg-[#0B1120] text-white">
          <Navbar />
          
          <div className="flex h-[calc(100vh-4rem)]">
            {/* 左侧股票列表 */}
            <aside className="w-72 border-r border-gray-800 flex flex-col">
              <div className="p-4 space-y-4 border-b border-gray-800">
                {/* 策略分析按钮 */}
                <button
                  onClick={() => router.push('/analysis')}
                  className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2"
                >
                  <LineChart className="w-5 h-5" />
                  <span>策略分析</span>
                </button>
                
                {/* 回测按钮 */}
                <button
                  onClick={() => router.push('/analysis/backtest')}
                  className="w-full py-2 px-4 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center space-x-2"
                >
                  <BarChart2 className="w-5 h-5" />
                  <span>策略回测</span>
                </button>
              </div>
              
              {/* 股票列表可滚动区域 */}
              <div className="flex-1 overflow-y-auto">
                <StockList />
              </div>
            </aside>
            
            {/* 主内容区域 */}
            <main className="flex-1 p-4">
              {/* 股票标题和基本信息 */}
              <div className="flex justify-between items-start sticky top-0 bg-[#0B1120] z-10 pb-4">
                <div>
                  <h1 className="text-2xl font-bold">{selectedStock}</h1>
                  <p className="text-gray-400">{quote?.name}</p>
                </div>
                <div className="flex items-center space-x-4">
                  <ChartSettings config={chartConfig} onConfigChange={setChartConfig} />
                </div>
              </div>
              
              {/* 图表和市场数据并排布局 */}
              <div className="flex gap-4">
                {/* 左侧图表区域 */}
                <div className="flex-1">
                  <div className="bg-[#141B2D] rounded-lg p-4">
                    {isLoadingQuote ? (
                      <div className="h-[600px] flex items-center justify-center">
                        <span>加载中...</span>
                      </div>
                    ) : quoteError ? (
                      <div className="h-[600px] flex items-center justify-center text-red-500">
                        加载失败: {quoteError.message}
                      </div>
                    ) : (
                      <KLineChart
                        data={klineData}
                        timeframe={chartConfig.timeframe}
                        onTimeframeChange={(tf) => setChartConfig(prev => ({ ...prev, timeframe: tf }))}
                        chartConfig={chartConfig}
                      />
                    )}
                  </div>
                </div>
                
                {/* 右侧市场数据 */}
                <div className="w-80 space-y-4">
                  {quote && (
                    <>
                      <MarketData data={quote} />
                      <ExtendedMarketData data={quote} />
                    </>
                  )}
                </div>
              </div>
            </main>
          </div>
        </div>
      </ThemeProvider>
    </QueryClientProvider>
  );
} 