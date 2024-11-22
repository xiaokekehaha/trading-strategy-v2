'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import type { PortfolioAnalysisResult } from '@/types/portfolio';
import PortfolioOptimizationComponent from '@/components/PortfolioOptimization';
import PortfolioAllocationComponent from '@/components/PortfolioAllocation';
import PortfolioChartComponent from '@/components/PortfolioChart';
import PortfolioMetricsComponent from '@/components/PortfolioMetrics';

export default function PortfolioPage() {
  const [result, setResult] = useState<PortfolioAnalysisResult | null>(null);

  const handleOptimized = (data: PortfolioAnalysisResult) => {
    setResult(data);
  };

  return (
    <div className="container mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">投资组合优化</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <PortfolioOptimizationComponent onOptimized={handleOptimized} />
        </div>
        
        {result && (
          <div className="space-y-6">
            <PortfolioAllocationComponent allocation={result.optimization.optimal_weights} />
            <PortfolioMetricsComponent metrics={result.metrics} />
          </div>
        )}
      </div>
      
      {result && (
        <div className="mt-8">
          <PortfolioChartComponent result={result} />
        </div>
      )}
    </div>
  );
} 