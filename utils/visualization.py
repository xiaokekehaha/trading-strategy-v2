import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

class PortfolioVisualizer:
    def __init__(self, prices: pd.DataFrame, weights: np.ndarray, returns: np.ndarray):
        self.prices = prices
        self.weights = weights
        self.returns = returns
        
    def plot_efficient_frontier(self, samples: dict) -> go.Figure:
        # 确保数据是numpy数组
        returns = np.array(samples['portfolio_returns'])
        sharpes = np.array(samples['sharpe'])
        
        # 计算每个样本的风险和收益
        vols = np.std(returns, axis=0)
        rets = np.mean(returns, axis=0)
        
        # 转换为年化数据
        vols_annual = (vols * np.sqrt(252)).reshape(-1)  # 确保是1D数组
        rets_annual = (rets * 252).reshape(-1)  # 确保是1D数组
        sharpes = sharpes.reshape(-1)  # 确保是1D数组
        
        # 创建有效前沿散点图
        fig = go.Figure()
        
        # 添加所有采样点
        scatter_data = pd.DataFrame({
            'Volatility': vols_annual,
            'Return': rets_annual,
            'Sharpe': sharpes
        })
        
        fig.add_trace(go.Scatter(
            x=scatter_data['Volatility'],
            y=scatter_data['Return'],
            mode='markers',
            marker=dict(
                size=8,
                color=scatter_data['Sharpe'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='夏普比率')
            ),
            name='采样组合'
        ))
        
        # 标记最优组合点
        optimal_idx = np.argmax(sharpes)
        fig.add_trace(go.Scatter(
            x=[scatter_data['Volatility'].iloc[optimal_idx]],
            y=[scatter_data['Return'].iloc[optimal_idx]],
            mode='markers',
            marker=dict(
                size=15,
                symbol='star',
                color='red'
            ),
            name='最优组合'
        ))
        
        fig.update_layout(
            title='投资组合有效前沿',
            xaxis_title='年化波动率',
            yaxis_title='年化收益率',
            template='plotly_white',
            showlegend=True,
            xaxis=dict(
                tickformat='.1%',
                title_font=dict(size=14),
                tickfont=dict(size=12)
            ),
            yaxis=dict(
                tickformat='.1%',
                title_font=dict(size=14),
                tickfont=dict(size=12)
            )
        )
        
        return fig
    
    def plot_weights_pie(self) -> go.Figure:
        # 创建权重数据框
        weights_df = pd.DataFrame({
            'Asset': self.prices.columns,
            'Weight': self.weights
        })
        
        # 过滤掉权重太小的资产
        weights_df = weights_df[weights_df['Weight'] >= 0.01]
        
        # 创建饼图
        fig = go.Figure(data=[go.Pie(
            labels=weights_df['Asset'],
            values=weights_df['Weight'],
            hole=.3,
            textinfo='label+percent',
            textposition='inside',
            insidetextorientation='radial'
        )])
        
        fig.update_layout(
            title=dict(
                text='最优资产配置权重',
                font=dict(size=16)
            ),
            template='plotly_white',
            showlegend=False,
            annotations=[dict(
                text='权重配置',
                x=0.5,
                y=0.5,
                font_size=20,
                showarrow=False
            )]
        )
        
        return fig
    
    def get_portfolio_stats(self) -> dict:
        """计算组合的关键统计指标"""
        portfolio_returns = np.dot(self.returns, self.weights)
        annual_return = float(np.mean(portfolio_returns) * 252)
        annual_vol = float(np.std(portfolio_returns) * np.sqrt(252))
        sharpe_ratio = float(annual_return / annual_vol)
        
        return {
            'expected_return': annual_return * 100,  # 转换为百分比
            'volatility': annual_vol * 100,
            'sharpe_ratio': sharpe_ratio
        }