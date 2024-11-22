import React, { useState } from 'react';
import { OptimizationForm } from '../components/OptimizationForm';
import { EfficientFrontier, WeightsPie } from '../components/PortfolioCharts';
import { PortfolioData, OptimizationFormData } from '../types/portfolio';
import { Progress } from '../components/Progress';

export const Portfolio: React.FC = () => {
  const [data, setData] = useState<PortfolioData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  const handleOptimize = async (formData: OptimizationFormData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // 开始轮询进度
      const progressInterval = setInterval(async () => {
        const response = await fetch('/progress');
        const data = await response.json();
        setProgress(data.progress);
      }, 500);

      // 发送优化请求
      const response = await fetch('/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          // 确保数值类型正确
          target_return: Number(formData.target_return),
          risk_free_rate: Number(formData.risk_free_rate),
          lookback_years: Number(formData.lookback_years)
        })
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      if (result.error) {
        throw new Error(result.error);
      }

      setData(result);
      setProgress(100);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : '优化过程中出现错误');
      console.error('Optimization error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">资产组合优化系统</h1>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-8">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <OptimizationForm onSubmit={handleOptimize} isLoading={isLoading} />
        </div>

        {data && (
          <div>
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">优化结果摘要</h2>
              <dl className="grid grid-cols-2 gap-4">
                <div>
                  <dt className="text-sm font-medium text-gray-500">预期年化收益率</dt>
                  <dd className="mt-1 text-3xl font-semibold text-gray-900">
                    {data.stats.expected_return.toFixed(2)}%
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">年化波动率</dt>
                  <dd className="mt-1 text-3xl font-semibold text-gray-900">
                    {data.stats.volatility.toFixed(2)}%
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">夏普比率</dt>
                  <dd className="mt-1 text-3xl font-semibold text-gray-900">
                    {data.stats.sharpe_ratio.toFixed(2)}
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        )}
      </div>

      {isLoading && <Progress value={progress} />}

      {data && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">有效前沿</h2>
              <EfficientFrontier data={data} />
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">最优权重配置</h2>
              <WeightsPie data={data} />
            </div>
          </div>

          {/* 其他数据展示组件 */}
        </>
      )}
    </div>
  );
}; 