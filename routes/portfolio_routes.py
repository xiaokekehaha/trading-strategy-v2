from flask import Blueprint, request, jsonify, render_template
from services.optimizer_service import OptimizerService
from services.optimization_history import OptimizationHistory
from data.stock_data import StockDataManager
from data.data_loader import DataLoader
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import yaml

portfolio_bp = Blueprint('portfolio', __name__)
progress = 0
history_manager = OptimizationHistory()

def update_progress(value):
    global progress
    progress = int(value)

def convert_to_json_serializable(obj):
    """转换数据为JSON可序列化格式"""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient='records')
    return obj

def load_config():
    """加载配置"""
    try:
        with open('configs/config.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        # 返回默认配置
        return {
            'data': {
                'stock_path': "data/raw/stocks.csv",
                'traditional_path': "data/raw/traditional.csv",
                'start_date': "2018-01-01",
                'end_date': "2023-12-31"
            },
            'optimization': {
                'risk_free_rate': 0.02,
                'target_return': 0.10
            },
            'mcmc': {
                'draws': 2000,
                'chains': 2,
                'tune': 1000,
                'random_seed': 42
            }
        }

@portfolio_bp.route('/progress')
def get_progress():
    global progress
    return jsonify({'progress': progress})

@portfolio_bp.route('/versions', methods=['GET'])
def get_versions():
    """获取所有优化版本"""
    versions_df = history_manager.get_all_versions()
    return jsonify(convert_to_json_serializable(versions_df))

@portfolio_bp.route('/versions/<int:version>', methods=['GET'])
def get_version(version):
    """获取指定版本的优化结果"""
    data = history_manager.get_optimization(version)
    if not data:
        return jsonify({'error': '版本不存在'}), 404
    return jsonify(convert_to_json_serializable(data))

@portfolio_bp.route('/versions/compare', methods=['GET'])
def compare_versions():
    """比较两个版本"""
    version1 = request.args.get('v1', type=int)
    version2 = request.args.get('v2', type=int)
    
    if not version1 or not version2:
        return jsonify({'error': '请指定要比较的版本'}), 400
        
    try:
        comparison = history_manager.compare_versions(version1, version2)
        return jsonify(convert_to_json_serializable(comparison))
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@portfolio_bp.route('/versions/latest', methods=['GET'])
def get_latest_version():
    """获取最新的优化结果"""
    data = history_manager.get_latest_optimization()
    if not data:
        return jsonify({'error': '没有优化历史'}), 404
    return jsonify(convert_to_json_serializable(data))

@portfolio_bp.route('/', methods=['GET', 'POST'])
def index():
    """股票组合优化页面"""
    global progress
    if request.method == 'GET':
        progress = 0
        return render_template('portfolio.html')
    
    try:
        progress = 0
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
            
        # 验证参数
        try:
            symbols = str(data.get('symbols', '')).strip()
            lookback_years = int(data.get('lookback_years', 0))
            target_return = float(data.get('target_return', 0))
            risk_free_rate = float(data.get('risk_free_rate', 0))
            optimizer_type = str(data.get('optimizer_type', 'bayesian'))
            
            if not symbols:
                return jsonify({'error': '请输入股票代码'}), 400
            if lookback_years < 1 or lookback_years > 10:
                return jsonify({'error': '回溯期必须在1-10年之间'}), 400
            if target_return <= 0:
                return jsonify({'error': '目标收益率必须大于0'}), 400
            if risk_free_rate < 0:
                return jsonify({'error': '无风险利率不能为负'}), 400
                
        except (ValueError, TypeError) as e:
            return jsonify({'error': f'参数格式错误: {str(e)}'}), 400
            
        # 获取股票数据
        try:
            symbols_list = [s.strip() for s in symbols.split(',') if s.strip()]
            start_date = (datetime.now() - timedelta(days=365*lookback_years)).strftime('%Y-%m-%d')
            
            progress = 10
            stock_manager = StockDataManager(symbols_list)
            prices, returns = stock_manager.fetch_data(start_date)
            
        except Exception as e:
            return jsonify({'error': f'获取股票数据失败: {str(e)}'}), 400
            
        try:
            progress = 30
            # 执行优化
            optimization_result = OptimizerService.optimize(
                optimizer_type=optimizer_type,
                returns=returns.values,
                risk_free_rate=risk_free_rate/100,
                progress_callback=lambda p: update_progress(30 + p * 0.6)
            )
            
            # 保存优化结果
            version = history_manager.save_optimization(
                symbols=symbols_list,
                weights={s: float(w) for s, w in zip(symbols_list, optimization_result['weights'])},
                params={
                    'risk_free_rate': risk_free_rate,
                    'target_return': target_return,
                    'lookback_years': lookback_years,
                    'optimizer_type': optimizer_type
                },
                metrics=optimization_result['metrics'],
                optimizer_type=optimizer_type
            )
            
            weights = optimization_result['weights']
            
            # 生成调仓建议
            current_weights = {symbol: 1/len(symbols_list) for symbol in symbols_list}
            optimal_weights = {symbol: float(w) for symbol, w in zip(symbols_list, weights)}
            rebalance_suggestions = stock_manager.get_rebalance_suggestions(
                current_weights, optimal_weights
            )
            
            # 获取分析数据
            analysis = stock_manager.get_portfolio_analysis()
            
            progress = 100
            
            # 返回结果
            response_data = {
                'version': version,
                'weights_data': {
                    'weights': convert_to_json_serializable(weights),
                    'assets': symbols_list
                },
                'stats': convert_to_json_serializable(optimization_result['metrics']),
                'rebalance_suggestions': convert_to_json_serializable(rebalance_suggestions),
                'analysis': convert_to_json_serializable(analysis),
                'frontier_data': {
                    'volatilities': convert_to_json_serializable(optimization_result.get('volatilities', [])),
                    'returns': convert_to_json_serializable(optimization_result.get('returns', [])),
                    'sharpes': convert_to_json_serializable(optimization_result.get('sharpes', []))
                }
            }
            
            return jsonify(response_data)
            
        except Exception as e:
            return jsonify({'error': f'优化过程失败: {str(e)}'}), 400
            
    except Exception as e:
        print(f"全局错误: {str(e)}")
        progress = 0
        return jsonify({'error': f"优化过程中出现错误: {str(e)}"}), 500 

@portfolio_bp.route('/optimize', methods=['POST'])
def optimize():
    """股票组合优化"""
    global progress
    try:
        progress = 0
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
            
        # 验证参数
        try:
            symbols = str(data.get('symbols', '')).strip()
            lookback_years = int(data.get('lookback_years', 0))
            target_return = float(data.get('target_return', 0))
            risk_free_rate = float(data.get('risk_free_rate', 0))
            optimizer_type = str(data.get('optimizer_type', 'bayesian'))
            
            if not symbols:
                return jsonify({'error': '请输入股票代码'}), 400
            if lookback_years < 1 or lookback_years > 10:
                return jsonify({'error': '回溯期必须在1-10年之间'}), 400
            if target_return <= 0:
                return jsonify({'error': '目标收益率必须大于0'}), 400
            if risk_free_rate < 0:
                return jsonify({'error': '无风险利率不能为负'}), 400
                
        except (ValueError, TypeError) as e:
            return jsonify({'error': f'参数格式错误: {str(e)}'}), 400
            
        # 获取股票数据
        try:
            symbols_list = [s.strip() for s in symbols.split(',') if s.strip()]
            start_date = (datetime.now() - timedelta(days=365*lookback_years)).strftime('%Y-%m-%d')
            
            progress = 10
            stock_manager = StockDataManager(symbols_list)
            prices, returns = stock_manager.fetch_data(start_date)
            
        except Exception as e:
            return jsonify({'error': f'获取股票数据失败: {str(e)}'}), 400
            
        try:
            progress = 30
            # 执行优化
            optimization_result = OptimizerService.optimize(
                optimizer_type=optimizer_type,
                returns=returns.values,
                risk_free_rate=risk_free_rate/100,
                progress_callback=lambda p: update_progress(30 + p * 0.6)
            )
            
            # 保存优化结果
            version = history_manager.save_optimization(
                symbols=symbols_list,
                weights={s: float(w) for s, w in zip(symbols_list, optimization_result['weights'])},
                params={
                    'risk_free_rate': risk_free_rate,
                    'target_return': target_return,
                    'lookback_years': lookback_years,
                    'optimizer_type': optimizer_type
                },
                metrics=optimization_result['metrics'],
                optimizer_type=optimizer_type
            )
            
            weights = optimization_result['weights']
            
            # 生成调仓建议
            current_weights = {symbol: 1/len(symbols_list) for symbol in symbols_list}
            optimal_weights = {symbol: float(w) for symbol, w in zip(symbols_list, weights)}
            rebalance_suggestions = stock_manager.get_rebalance_suggestions(
                current_weights, optimal_weights
            )
            
            # 获取分析数据
            analysis = stock_manager.get_portfolio_analysis()
            
            progress = 100
            
            # 返回结果
            response_data = {
                'version': version,
                'weights_data': {
                    'weights': convert_to_json_serializable(weights),
                    'assets': symbols_list
                },
                'stats': convert_to_json_serializable(optimization_result['metrics']),
                'rebalance_suggestions': convert_to_json_serializable(rebalance_suggestions),
                'analysis': convert_to_json_serializable(analysis),
                'frontier_data': {
                    'volatilities': convert_to_json_serializable(optimization_result.get('volatilities', [])),
                    'returns': convert_to_json_serializable(optimization_result.get('returns', [])),
                    'sharpes': convert_to_json_serializable(optimization_result.get('sharpes', []))
                }
            }
            
            return jsonify(response_data)
            
        except Exception as e:
            return jsonify({'error': f'优化过程失败: {str(e)}'}), 400
            
    except Exception as e:
        print(f"全局错误: {str(e)}")
        progress = 0
        return jsonify({'error': f"优化过程中出现错误: {str(e)}"}), 500 

@portfolio_bp.route('/optimize_traditional', methods=['POST'])
def optimize_traditional():
    """传统资产组合优化"""
    global progress
    try:
        progress = 0
        config = load_config()
        
        # 验证参数
        try:
            data = request.get_json()  # 改为获取JSON数据
            if not data:
                return jsonify({'error': '无效的请求数据'}), 400
                
            target_return = float(data['target_return'])
            risk_free_rate = float(data['risk_free_rate'])
            
            if target_return <= 0:
                return jsonify({'error': '目标收益率必须大于0'}), 400
            if risk_free_rate < 0:
                return jsonify({'error': '无风险利率不能为负'}), 400
                
        except (ValueError, TypeError, KeyError) as e:
            return jsonify({'error': f'参数格式错误: {str(e)}'}), 400
            
        # 加载传统资产数据
        try:
            progress = 10
            data_loader = DataLoader(config, data_type='traditional')
            prices, returns = data_loader.load_data()
            asset_list = prices.columns.tolist()  # 获取资产列表
            
        except Exception as e:
            return jsonify({'error': f'获取数据失败: {str(e)}'}), 400
            
        try:
            progress = 30
            # 执行优化
            optimization_result = OptimizerService.optimize(
                optimizer_type='bayesian',  # 传统资产默认使用贝叶斯优化
                returns=returns,
                risk_free_rate=risk_free_rate/100,
                progress_callback=lambda p: update_progress(30 + p * 0.6)
            )
            
            weights = optimization_result['weights']
            
            # 保存优化结果
            version = history_manager.save_optimization(
                symbols=asset_list,
                weights={s: float(w) for s, w in zip(asset_list, weights)},
                params={
                    'risk_free_rate': risk_free_rate,
                    'target_return': target_return,
                    'optimizer_type': 'bayesian'
                },
                metrics=optimization_result['metrics'],
                optimizer_type='traditional'  # 标记为传统资产优化
            )
            
            # 生成调仓建议
            current_weights = {symbol: 1/len(asset_list) for symbol in asset_list}
            optimal_weights = {symbol: float(w) for symbol, w in zip(asset_list, weights)}
            
            # 计算前端所需数据
            returns_data = optimization_result.get('samples', {}).get('portfolio_returns', [])
            if len(returns_data) > 0:
                vols = np.std(returns_data, axis=0) * np.sqrt(252)
                rets = np.mean(returns_data, axis=0) * np.sqrt(252)
                sharpes = optimization_result.get('samples', {}).get('sharpe', [])
            else:
                # 如果没有采样数据，使用单点数据
                portfolio_returns = np.dot(returns, weights)
                vols = [float(np.std(portfolio_returns) * np.sqrt(252))]
                rets = [float(np.mean(portfolio_returns) * np.sqrt(252))]
                sharpes = [optimization_result['metrics']['sharpe_ratio']]
            
            progress = 100
            
            # 返回结果
            response_data = {
                'version': version,
                'weights_data': {
                    'weights': convert_to_json_serializable(weights),
                    'assets': asset_list
                },
                'stats': convert_to_json_serializable(optimization_result['metrics']),
                'frontier_data': {
                    'volatilities': convert_to_json_serializable(vols),
                    'returns': convert_to_json_serializable(rets),
                    'sharpes': convert_to_json_serializable(sharpes)
                }
            }
            
            return jsonify(response_data)
            
        except Exception as e:
            return jsonify({'error': f'优化过程失败: {str(e)}'}), 400
            
    except Exception as e:
        print(f"全局错误: {str(e)}")
        progress = 0
        return jsonify({'error': f"优化过程中出现错误: {str(e)}"}), 500

@portfolio_bp.route('/traditional', methods=['GET', 'POST'])
def traditional():
    """传统资产组合优化页面"""
    global progress
    if request.method == 'GET':
        progress = 0
        return render_template('traditional.html')
    
    try:
        progress = 0
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
            
        # 验证参数
        try:
            target_return = float(data.get('target_return', 0))
            risk_free_rate = float(data.get('risk_free_rate', 0))
            
            if target_return <= 0:
                return jsonify({'error': '目标收益率必须大于0'}), 400
            if risk_free_rate < 0:
                return jsonify({'error': '无风险利率不能为负'}), 400
                
        except (ValueError, TypeError) as e:
            return jsonify({'error': f'参数格式错误: {str(e)}'}), 400
            
        # 加载传统资产数据
        try:
            progress = 10
            data_loader = DataLoader(load_config(), data_type='traditional')
            prices, returns = data_loader.load_data()
            # 确保returns是2D数组
            if len(returns.shape) == 1:
                returns = returns.reshape(-1, 1)
            asset_list = prices.columns.tolist()  # 获取资产列表
            
        except Exception as e:
            return jsonify({'error': f'获取数据失败: {str(e)}'}), 400
            
        try:
            progress = 30
            # 执行优化
            optimization_result = OptimizerService.optimize(
                optimizer_type='bayesian',  # 传统资产默认使用贝叶斯优化
                returns=returns,
                risk_free_rate=risk_free_rate/100,
                progress_callback=lambda p: update_progress(30 + p * 0.6)
            )
            
            weights = optimization_result['weights']
            
            # 保存优化结果
            version = history_manager.save_optimization(
                symbols=asset_list,
                weights={s: float(w) for s, w in zip(asset_list, weights)},
                params={
                    'risk_free_rate': risk_free_rate,
                    'target_return': target_return,
                    'optimizer_type': 'bayesian'
                },
                metrics=optimization_result['metrics'],
                optimizer_type='traditional'  # 标记为传统资产优化
            )
            
            # 生成调仓建议
            current_weights = {symbol: 1/len(asset_list) for symbol in asset_list}
            optimal_weights = {symbol: float(w) for symbol, w in zip(asset_list, weights)}
            
            # 计算前端所需数据
            returns_data = optimization_result.get('samples', {}).get('portfolio_returns', [])
            if len(returns_data) > 0:
                vols = np.std(returns_data, axis=0) * np.sqrt(252)
                rets = np.mean(returns_data, axis=0) * np.sqrt(252)
                sharpes = optimization_result.get('samples', {}).get('sharpe', [])
            else:
                # 如果没有采样数据，使用单点数据
                portfolio_returns = np.dot(returns, weights)
                vols = [float(np.std(portfolio_returns) * np.sqrt(252))]
                rets = [float(np.mean(portfolio_returns) * np.sqrt(252))]
                sharpes = [optimization_result['metrics']['sharpe_ratio']]
            
            progress = 100
            
            # 返回结果
            response_data = {
                'version': version,
                'weights_data': {
                    'weights': convert_to_json_serializable(weights),
                    'assets': asset_list
                },
                'stats': convert_to_json_serializable(optimization_result['metrics']),
                'frontier_data': {
                    'volatilities': convert_to_json_serializable(vols),
                    'returns': convert_to_json_serializable(rets),
                    'sharpes': convert_to_json_serializable(sharpes)
                }
            }
            
            return jsonify(response_data)
            
        except Exception as e:
            return jsonify({'error': f'优化过程失败: {str(e)}'}), 400
            
    except Exception as e:
        print(f"全局错误: {str(e)}")
        progress = 0
        return jsonify({'error': f"优化过程中出现错误: {str(e)}"}), 500