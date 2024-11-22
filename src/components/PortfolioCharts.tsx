import React from 'react';
import Plot from 'react-plotly.js';
import { PortfolioData } from '../types/portfolio';

interface ChartProps {
  data: PortfolioData;
}

export const EfficientFrontier: React.FC<ChartProps> = ({ data }) => {
  const { volatilities, returns, sharpes } = data.frontier_data;
  const optimalIdx = sharpes.indexOf(Math.max(...sharpes));

  return (
    <Plot
      data={[
        {
          x: volatilities,
          y: returns,
          mode: 'markers',
          type: 'scatter',
          marker: {
            size: 8,
            color: sharpes,
            colorscale: 'Viridis',
            showscale: true,
            colorbar: { title: '夏普比率' }
          },
          name: '采样组合'
        },
        {
          x: [volatilities[optimalIdx]],
          y: [returns[optimalIdx]],
          mode: 'markers',
          type: 'scatter',
          marker: {
            size: 15,
            symbol: 'star',
            color: 'red'
          },
          name: '最优组合'
        }
      ]}
      layout={{
        title: '投资组合有效前沿',
        xaxis: {
          title: '年化波动率',
          tickformat: '.1%'
        },
        yaxis: {
          title: '年化收益率',
          tickformat: '.1%'
        },
        template: 'plotly_white',
        showlegend: true
      }}
      className="w-full h-[400px]"
    />
  );
};

export const WeightsPie: React.FC<ChartProps> = ({ data }) => {
  const { weights, assets } = data.weights_data;
  const threshold = 0.01;
  
  const significantWeights = weights.filter(w => w >= threshold);
  const significantAssets = assets.filter((_, i) => weights[i] >= threshold);

  return (
    <Plot
      data={[
        {
          values: significantWeights,
          labels: significantAssets,
          type: 'pie',
          hole: 0.3,
          textinfo: 'label+percent',
          textposition: 'inside',
          insidetextorientation: 'radial'
        }
      ]}
      layout={{
        title: '最优资产配置权重',
        annotations: [{
          text: '权重配置',
          showarrow: false,
          font: { size: 20 },
          x: 0.5,
          y: 0.5
        }],
        showlegend: false
      }}
      className="w-full h-[400px]"
    />
  );
}; 