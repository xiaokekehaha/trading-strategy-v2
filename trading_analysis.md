# 量化交易分析平台使用指南

## 1. 系统概述

量化交易分析平台是一个集成了数据获取、策略回测、投资组合优化的完整解决方案。系统支持多种交易策略，包括趋势类、波动类、形态类和动量类策略。

### 1.1 主要功能
- 股票数据实时获取和分析
- 多种技术指标计算
- 策略回测和评估
- 投资组合优化
- 可视化分析结果

## 2. 策略类型

### 2.1 趋势类策略
- **移动平均线交叉策略**
  ```python
  # 使用示例
  from models.strategies.indicators.moving_average import MovingAverageCrossStrategy
  
  strategy = MovingAverageCrossStrategy(short_window=5, long_window=20)
  results = strategy.backtest(data)
  ```

- **MACD策略**
  ```python
  from models.strategies.indicators.macd import MACDStrategy
  
  strategy = MACDStrategy(fast_period=12, slow_period=26, signal_period=9)
  results = strategy.backtest(data)
  ```

### 2.2 波动类策略
- **布林带策略**
  ```python
  from models.strategies.indicators.bollinger_bands import BollingerBandsStrategy
  
  strategy = BollingerBandsStrategy(window=20, num_std=2.0)
  results = strategy.backtest(data)
  ```

### 2.3 形态类策略
- **BarUpDn策略**
  ```python
  from models.strategies.basic.bar_up_down import BarUpDnStrategy
  
  strategy = BarUpDnStrategy(n_bars=3)
  results = strategy.backtest(data)
  ```

### 2.4 动量类策略
- **动量策略**
  ```python
  from models.strategies.momentum.momentum import MomentumStrategy
  
  strategy = MomentumStrategy(lookback_period=12)
  results = strategy.backtest(data)
  ```

## 3. 回测系统使用

### 3.1 单策略回测
```python
from services.backtest_service import BacktestService

backtest_service = BacktestService()
results = await backtest_service.run_backtest(
    symbol="AAPL",
    start_date="2022-01-01",
    end_date="2023-01-01",
    strategy={
        "name": "bollinger_bands",
        "params": {"window": 20, "num_std": 2.0}
    }
)
```

### 3.2 策略评估指标
- **总收益率**: 策略在回测期间的总收益
- **年化收益率**: 收益率年化后的结果
- **夏普比率**: 超额收益与波动率的比值
- **最大回撤**: 最大的亏损幅度
- **胜率**: 盈利交易占总交易的比例

## 4. 数据管理

### 4.1 数据获取
```python
from data.stock_data import StockDataManager

stock_manager = StockDataManager(["AAPL", "GOOGL"])
prices, returns = stock_manager.fetch_data("2022-01-01", "2023-01-01")
```

### 4.2 数据存储
```python
from services.file_storage import FileStorageService

storage = FileStorageService()
storage.save_stock_data("AAPL", data)
```

## 5. 前端界面使用

### 5.1 策略分析页面
- 选择股票代码
- 设置回测时间范围
- 选择策略类型
- 配置策略参数
- 查看回测结果和图表

### 5.2 投资组合页面
- 添加多个股票
- 配置多个策略
- 设置组合权重
- 查看组合分析结果

## 6. API接口

### 6.1 回测接口
```bash
# 运行回测
POST /api/backtest/run
{
    "symbol": "AAPL",
    "start_date": "2022-01-01",
    "end_date": "2023-01-01",
    "strategy": {
        "name": "bollinger_bands",
        "params": {
            "window": 20,
            "num_std": 2.0
        }
    }
}

# 获取回测结果
GET /api/backtest/results/{backtest_id}
```

### 6.2 股票数据接口
```bash
# 获取股票价格
GET /api/stocks/{symbol}/price?start_date=2022-01-01&end_date=2023-01-01

# 获取技术指标
GET /api/stocks/{symbol}/indicators?indicators=ma,rsi,macd
```

## 7. 最佳实践

### 7.1 策略开发建议
- 使用BaseStrategy作为基类开发新策略
- 实现generate_signals方法生成交易信号
- 添加策略参数的验证逻辑
- 编写完整的策略文档

### 7.2 回测建议
- 使用足够长的回测周期
- 考虑交易成本和滑点
- 进行参数敏感性分析
- 避免过度拟合

### 7.3 风险控制
- 设置止损止盈
- 控制单次交易规模
- 分散投资组合
- 监控回撤指标