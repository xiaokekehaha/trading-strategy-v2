# 贝叶斯投资组合优化系统

基于贝叶斯方法和MCMC采样的投资组合优化系统，使用 PyMC 实现。

## 功能特点

- 基于贝叶斯方法的投资组合优化
- MCMC采样获取最优权重
- 实时进度显示
- 交互式可视化
- 完整的测试覆盖

## 项目结构

```
portfolio_optimization/
├── configs/
│   └── config.yaml          # 配置文件
├── data/
│   ├── data_loader.py       # 数据加载器
│   ├── generate_sample_data.py  # 样本数据生成
│   └── raw/                 # 原始数据目录
│       └── prices.csv       # 价格数据
├── models/
│   ├── bayesian_model.py    # 贝叶斯模型
│   └── mcmc_sampler.py      # MCMC采样器
├── utils/
│   └── visualization.py     # 可视化工具
├── templates/
│   └── portfolio.html       # Web界面模板
├── tests/
│   └── test_portfolio.py    # 测试用例
├── main.py                  # 主程序入口
└── requirements.txt         # 依赖包列表
```

## 核心模块说明

### 1. 贝叶斯模型 (models/bayesian_model.py)
- 使用 PyMC 构建贝叶斯模型
- 包含权重的 Dirichlet 先验
- 使用 LKJCholeskyCov 生成协方差矩阵
- 计算组合收益率和夏普比率

### 2. MCMC采样器 (models/mcmc_sampler.py)
- 实现 MCMC 采样过程
- 支持进度回调
- 获取最优权重配置

### 3. 数据处理 (data/data_loader.py)
- 加载历史价格数据
- 计算收益率
- 数据预处理

### 4. 可视化 (utils/visualization.py)
- 绘制有效前沿
- 生成权重配置饼图
- 计算组合统计指标

### 5. Web界面 (templates/portfolio.html)
- 参数设置表单
- 实时进度显示
- 交互式图表展示
- 优化结果展示

## 配置说明 (configs/config.yaml)

```yaml
data:
  path: "data/raw/prices.csv"    # 数据文件路径
  start_date: "2018-01-01"       # 起始日期
  end_date: "2023-12-31"         # 结束日期

optimization:
  risk_free_rate: 0.02           # 无风险利率
  target_return: 0.10            # 目标收益率

mcmc:
  draws: 10000                   # 采样次数
  chains: 4                      # 链数量
  tune: 1000                     # 调优步数
  random_seed: 42                # 随机种子
```

## 使用方法

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 生成样本数据（可选）：
```bash
python data/generate_sample_data.py
```

3. 运行系统：
```bash
python main.py
```

4. 访问Web界面：
```
http://localhost:5000
```

## API说明

### 主要接口

1. `/` (GET)
- 返回优化系统的Web界面

2. `/` (POST)
- 接收优化参数并执行计算
- 返回优化结果的JSON数据

3. `/progress` (GET)
- 返回当前计算进度

### 返回数据格式

```json
{
    "frontier_data": {
        "volatilities": [...],
        "returns": [...],
        "sharpes": [...]
    },
    "weights_data": {
        "weights": [...],
        "assets": [...]
    },
    "stats": {
        "expected_return": float,
        "volatility": float,
        "sharpe_ratio": float
    }
}
```

## 测试

运行测试：
```bash
pytest tests/test_portfolio.py
```

测试覆盖：
- 模型构建测试
- MCMC采样测试
- 真实数据测试
- 约束条件验证

## 注意事项

1. 数据要求：
   - CSV格式的价格数据
   - 日期索引
   - 资产名称列名

2. 性能考虑：
   - MCMC采样计算密集
   - 建议适当调整采样参数
   - 支持多链并行计算

3. 内存使用：
   - 大量数据时注意内存占用
   - 可通过配置调整采样参数

## 依赖包

- Flask
- PyMC
- NumPy
- Pandas
- Plotly
- PyYAML
- pytest

## 后续优化方向

1. 模型增强：
   - 添加更多先验分布选项
   - 支持多期优化
   - 加入交易成本约束

2. 性能优化：
   - 采样过程并行化
   - 数据处理优化
   - 缓存机制

3. 功能扩展：
   - 更多风险指标
   - 导出优化结果
   - 历史回测
```

这个文档提供了系统的完整说明，包括：
1. 项目结构
2. 核心模块说明
3. 配置参数
4. 使用方法
5. API接口
6. 测试说明
7. 注意事项
8. 后续优化方向

用户可以根据这个文档快速了解系统并开始使用。