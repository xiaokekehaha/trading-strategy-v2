import pandas as pd
import numpy as np
import os

def generate_price_data(data_type: str = 'stock'):
    """生成示例数据"""
    # 设置随机种子保证可重复性
    np.random.seed(42)
    
    # 生成日期索引
    dates = pd.date_range(start='2018-01-01', end='2023-12-31', freq='B')
    
    if data_type == 'traditional':
        # 传统资产配置
        assets = ['股票A', '股票B', '债券A', '商品A', 'ETF-A']
        annual_returns = np.array([0.10, 0.15, 0.05, 0.08, 0.12])
        annual_vols = np.array([0.20, 0.25, 0.08, 0.30, 0.18])
        output_path = 'data/raw/traditional.csv'
    else:
        # 股票配置
        assets = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
        annual_returns = np.array([0.15, 0.18, 0.20, 0.25, 0.22])
        annual_vols = np.array([0.25, 0.28, 0.30, 0.35, 0.32])
        output_path = 'data/raw/stocks.csv'
    
    # 生成相关系数矩阵
    corr = np.array([
        [1.0, 0.6, 0.2, 0.3, 0.7],
        [0.6, 1.0, 0.1, 0.4, 0.6],
        [0.2, 0.1, 1.0, 0.0, 0.3],
        [0.3, 0.4, 0.0, 1.0, 0.2],
        [0.7, 0.6, 0.3, 0.2, 1.0]
    ])
    
    # 计算日度参数
    daily_returns = annual_returns / 252
    daily_vols = annual_vols / np.sqrt(252)
    
    # 生成协方差矩阵
    cov = np.outer(daily_vols, daily_vols) * corr
    
    # 生成多元正态分布的收益率
    returns = np.random.multivariate_normal(
        mean=daily_returns,
        cov=cov,
        size=len(dates)
    )
    
    # 转换为价格
    prices = 100 * np.exp(np.cumsum(returns, axis=0))
    
    # 创建DataFrame
    df = pd.DataFrame(prices, index=dates, columns=assets)
    
    # 保存到CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path)
    
    return df

if __name__ == '__main__':
    prices = generate_price_data()
    print("模拟数据已生成：")
    print("\n前5行数据：")
    print(prices.head())
    print("\n基本统计信息：")
    returns = prices.pct_change().dropna()
    print("\n年化收益率：")
    print((1 + returns.mean()) ** 252 - 1)
    print("\n年化波动率：")
    print(returns.std() * np.sqrt(252)) 