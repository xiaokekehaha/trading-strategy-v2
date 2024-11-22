import pytest
import numpy as np
import pandas as pd
from models.bayesian_model import BayesianPortfolio
from models.mcmc_sampler import MCMCSampler
from data.data_loader import DataLoader
import yaml

@pytest.fixture
def sample_returns():
    # 生成模拟数据
    np.random.seed(42)
    n_days = 252
    n_assets = 4
    returns = np.random.normal(0.001, 0.02, (n_days, n_assets))
    return returns

@pytest.fixture
def config():
    with open('configs/config.yaml', 'r') as f:
        return yaml.safe_load(f)

@pytest.fixture
def real_data(config):
    data_loader = DataLoader(config)
    prices, returns = data_loader.load_data()
    return returns

def test_bayesian_portfolio(sample_returns):
    portfolio = BayesianPortfolio(sample_returns)
    model = portfolio.build_model()
    assert model is not None

def test_mcmc_sampling(sample_returns, config):
    portfolio = BayesianPortfolio(sample_returns)
    model = portfolio.build_model()
    
    sampler = MCMCSampler(model, config['mcmc'])
    trace = sampler.sample()
    
    assert 'weights' in trace
    assert 'sharpe' in trace
    assert 'portfolio_returns' in trace
    
    weights = sampler.get_optimal_weights()
    assert len(weights) == sample_returns.shape[1]
    assert np.isclose(np.sum(weights), 1.0)

def test_with_real_data(real_data, config):
    portfolio = BayesianPortfolio(real_data, risk_free_rate=config['optimization']['risk_free_rate'])
    model = portfolio.build_model()
    
    sampler = MCMCSampler(model, config['mcmc'])
    trace = sampler.sample()
    weights = sampler.get_optimal_weights()
    
    # 测试权重约束
    assert np.all(weights >= 0)  # 非负约束
    assert np.isclose(np.sum(weights), 1.0)  # 权重和为1
    
    # 测试夏普比率是否合理
    assert np.mean(trace['sharpe']) > -1  # 夏普比率应该在合理范围内