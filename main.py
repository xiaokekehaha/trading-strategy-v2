from flask import Flask, render_template, request, jsonify
import yaml
import numpy as np
from data.data_loader import DataLoader
from models.bayesian_model import BayesianPortfolio
from models.mcmc_sampler import MCMCSampler
from data.stock_data import StockDataManager
from datetime import datetime, timedelta

app = Flask(__name__)
progress = 0

def load_config():
    with open('configs/config.yaml', 'r') as f:
        return yaml.safe_load(f)

@app.route('/progress')
def get_progress():
    global progress
    return jsonify({'progress': progress})

@app.route('/', methods=['GET', 'POST'])
def index():
    global progress
    if request.method == 'GET':
        progress = 0
        return render_template('portfolio.html')
    
    try:
        progress = 0
        config = load_config()
        
        # 获取JSON数据
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
            
        # 验证必要字段
        required_fields = ['symbols', 'lookback_years', 'target_return', 'risk_free_rate']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必要字段: {field}'}), 400
        
        try:
            # 获取股票数据
            symbols = data['symbols'].strip().split(',')
            lookback_years = int(data['lookback_years'])
            start_date = (datetime.now() - timedelta(days=365*lookback_years)).strftime('%Y-%m-%d')
            
            progress = 10
            stock_manager = StockDataManager(symbols)
            prices, returns = stock_manager.fetch_data(start_date)
            
        except Exception as e:
            return jsonify({'error': f'获取股票数据失败: {str(e)}'}), 400
            
        try:
            progress = 30
            # 构建模型并采样
            portfolio = BayesianPortfolio(returns.values, 
                                        risk_free_rate=float(data['risk_free_rate'])/100)
            model = portfolio.build_model()
            
        except Exception as e:
            return jsonify({'error': f'构建模型失败: {str(e)}'}), 400
            
        try:
            progress = 40
            sampler = MCMCSampler(model, config['mcmc'])
            samples = sampler.sample(progress_callback=lambda p: update_progress(40 + p * 0.4))
            weights = sampler.get_optimal_weights()
            
        except Exception as e:
            return jsonify({'error': f'MCMC采样失败: {str(e)}'}), 400
            
        progress = 80
        # 生成调仓建议
        current_weights = {symbol: 1/len(symbols) for symbol in symbols}  # 假设当前等权重
        optimal_weights = {symbol: weight for symbol, weight in zip(symbols, weights)}
        rebalance_suggestions = stock_manager.get_rebalance_suggestions(
            current_weights, optimal_weights
        )
        
        # 获取股票池分析
        analysis = stock_manager.get_portfolio_analysis()
        
        # 计算前端所需数据
        returns_data = samples['portfolio_returns']
        vols = np.std(returns_data, axis=0) * np.sqrt(252)
        rets = np.mean(returns_data, axis=0) * 252
        sharpes = samples['sharpe']
        
        # 计算组合统计信息
        portfolio_returns = np.dot(returns.values, weights)
        annual_return = float(np.mean(portfolio_returns) * 252)
        annual_vol = float(np.std(portfolio_returns) * np.sqrt(252))
        sharpe_ratio = float((annual_return - float(data['risk_free_rate'])/100) / annual_vol)
        
        progress = 100
        
        return jsonify({
            'frontier_data': {
                'volatilities': vols.tolist(),
                'returns': rets.tolist(),
                'sharpes': sharpes.tolist()
            },
            'weights_data': {
                'weights': weights.tolist(),
                'assets': symbols
            },
            'stats': {
                'expected_return': annual_return * 100,
                'volatility': annual_vol * 100,
                'sharpe_ratio': sharpe_ratio
            },
            'rebalance_suggestions': rebalance_suggestions,
            'analysis': analysis
        })
                             
    except Exception as e:
        print(f"全局错误: {str(e)}")
        progress = 0
        return jsonify({'error': f"优化过程中出现错误: {str(e)}"}), 500

def update_progress(value):
    global progress
    progress = int(value)

# 添加新的路由
@app.route('/traditional')
def traditional():
    """传统资产组合优化页面"""
    return render_template('traditional.html')

@app.route('/optimize_traditional', methods=['POST'])
def optimize_traditional():
    global progress
    try:
        progress = 0
        config = load_config()
        
        # 获取表单数据并验证
        if not request.form:
            return jsonify({'error': '无效的请求数据'}), 400
            
        try:
            risk_free_rate = float(request.form['risk_free_rate']) / 100
            target_return = float(request.form['target_return']) / 100
        except (KeyError, ValueError) as e:
            return jsonify({'error': '参数格式错误'}), 400
        
        progress = 10
        # 加载数据
        try:
            data_loader = DataLoader(config)
            prices, returns = data_loader.load_data()
        except Exception as e:
            return jsonify({'error': f'数据加载失败: {str(e)}'}), 400
        
        progress = 30
        # 构建模型并采样
        try:
            portfolio = BayesianPortfolio(returns, risk_free_rate=risk_free_rate)
            model = portfolio.build_model()
        except Exception as e:
            return jsonify({'error': f'模型构建失败: {str(e)}'}), 400
        
        progress = 40
        try:
            sampler = MCMCSampler(model, config['mcmc'])
            samples = sampler.sample(progress_callback=lambda p: update_progress(40 + p * 0.4))
            weights = sampler.get_optimal_weights()
        except Exception as e:
            return jsonify({'error': f'MCMC采样失败: {str(e)}'}), 400
        
        progress = 80
        try:
            # 计算前端所需数据
            returns_data = samples['portfolio_returns']
            vols = np.std(returns_data, axis=0) * np.sqrt(252)
            rets = np.mean(returns_data, axis=0) * 252
            sharpes = samples['sharpe']
            
            # 计算组合统计信息
            portfolio_returns = np.dot(returns, weights)
            annual_return = float(np.mean(portfolio_returns) * 252)
            annual_vol = float(np.std(portfolio_returns) * np.sqrt(252))
            sharpe_ratio = float((annual_return - risk_free_rate) / annual_vol)
            
            # 获取资产名称
            asset_names = prices.columns.tolist()
            
            progress = 100
            
            return jsonify({
                'frontier_data': {
                    'volatilities': vols.tolist(),
                    'returns': rets.tolist(),
                    'sharpes': sharpes.tolist()
                },
                'weights_data': {
                    'weights': weights.tolist(),
                    'assets': asset_names
                },
                'stats': {
                    'expected_return': annual_return * 100,
                    'volatility': annual_vol * 100,
                    'sharpe_ratio': sharpe_ratio
                }
            })
            
        except Exception as e:
            return jsonify({'error': f'数据处理失败: {str(e)}'}), 400
                             
    except Exception as e:
        print(f"传统资产优化错误: {str(e)}")
        progress = 0
        return jsonify({'error': f"优化过程中出现错误: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True) 