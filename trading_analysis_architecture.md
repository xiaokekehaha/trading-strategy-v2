# 量化交易分析平台架构设计

## 1. 项目结构
```
project/
├── frontend/                      # 前端代码
│   ├── src/
│   │   ├── components/           # React组件
│   │   │   ├── PortfolioCharts.tsx    # 投资组合图表
│   │   │   └── OptimizationForm.tsx   # 优化表单
│   │   └── pages/               # 页面组件
│   │       ├── Portfolio.tsx     # 投资组合页面
│   │       └── Analysis.tsx      # 分析页面
│   └── templates/               # HTML模板
│       ├── portfolio.html       # 投资组合模板
│       └── traditional.html     # 传统分析模板
│
├── backend/                      # 后端代码
│   ├── data/                    # 数据层
│   │   ├── stock_data.py       # 股票数据管理
│   │   └── stocks/             # 股票数据文件
│   │       ├── AMZN.csv
│   │       └── ETF-A.csv
│   ├── models/                  # 模型层
│   │   ├── bayesian_model.py   # 贝叶斯模型
│   │   └── mcmc_sampler.py     # MCMC采样器
│   │   └── strategies/        # 策略层
│   │       ├── basic/          # 基础策略
│   │       │   ├── bar_up_down.py          # BarUpDn策略
│   │       │   ├── inside_bar.py           # InSide Bar策略
│   │       │   └── outside_bar.py          # OutSide Bar策略
│   │       ├── indicators/      # 指标策略
│   │       │   ├── bollinger_bands.py      # 布林带策略
│   │       │   ├── macd.py                 # MACD策略
│   │       │   └── moving_average.py       # 移动平均策略
│   │       ├── momentum/          # 动量策略
│   │       │   ├── momentum.py             # 动量策略
│   │       │   └── consecutive.py          # 连续上涨/下跌策略
│   │       ├── breakout/          # 突破策略
│   │       │   ├── channel_breakout.py     # 通道突破策略
│   │       │   └── pattern_breakout.py     # 形态突破策略
│   │       └── composite/          # 组合策略
│   │           ├── greedy.py              # 贪心策略
│   │           └── hybrid.py              # 混合策略
│   └── routes/                  # 路由层
│       └── portfolio_routes.py  # 投资组合路由
```

## 2. 技术栈

### 前端
- React + TypeScript
- TailwindCSS
- TradingView图表库
- Axios用于API请求

### 后端
- Python FastAPI
- Pandas用于数据处理
- NumPy用于数值计算
- yfinance获取股票数据

### 数据库
- PostgreSQL存储用户数据
- Redis缓存

## 3. 核心模块

### 数据管理模块 (data/stock_data.py)
- 股票数据获取和缓存
- 技术指标计算
- 数据清洗和预处理

### 分析模块 (models/strategies/)
```
strategies/
├── basic/
│   ├── bar_up_down.py          # BarUpDn策略
│   ├── inside_bar.py           # InSide Bar策略
│   └── outside_bar.py          # OutSide Bar策略
│
├── indicators/
│   ├── bollinger_bands.py      # 布林带策略
│   ├── macd.py                 # MACD策略
│   └── moving_average.py       # 移动平均策略
│
├── momentum/
│   ├── momentum.py             # 动量策略
│   └── consecutive.py          # 连续上涨/下跌策略
│
├── breakout/
│   ├── channel_breakout.py     # 通道突破策略
│   └── pattern_breakout.py     # 形态突破策略
│
└── composite/
    ├── greedy.py              # 贪心策略
    └── hybrid.py              # 混合策略
```

### 策略实现细节

1. **趋势类策略**
   - 移动平均线交叉策略 (MovingAvg Cross)
   - 移动平均双线交叉策略 (MovingAvg2Line Cross)
   - MACD策略

2. **波动类策略**
   - 布林带策略 (Bollinger Bands)
   - 布林带定向策略 (Bollinger Bands directed)
   - 通道突破策略 (Channel Break Out)

3. **形态类策略**
   - BarUpDn策略
   - InSide Bar策略
   - OutSide Bar策略

4. **动量类策略**
   - 动量策略 (Momentum)
   - 连续向上/向下策略 (Consecutive Up/Down)
   - 贪心策略 (Greedy)

### 策略评估指标
- 胜率
- 盈亏比
- 最大回撤
- 夏普比率
- 年化收益率

### 展示模块 (frontend/src/components/)
- 交互式图表展示
- 投资组合管理界面
- 分析结果可视化

## 4. API接口

### 股票数据
```
GET /api/stocks/{symbol}/price    # 获取股票价格
GET /api/stocks/{symbol}/indicators  # 获取技术指标
```

### 投资组合
```
GET /api/portfolio/analysis      # 获取组合分析
POST /api/portfolio/optimize     # 优化投资组合
```

### 回测
```
POST /api/backtest/run          # 运行回测
GET /api/backtest/results       # 获取回测结果
```

## 5. 数据流

1. 前端发起数据请求
2. 后端接收请求并验证
3. 数据层处理和计算
4. 返回结果到前端展示

## 6. 部署架构

- Nginx作为反向代理
- FastAPI处理API请求
- Redis缓存热点数据
- PostgreSQL存储持久化数据