import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from sklearn.linear_model import LinearRegression
import logging

logger = logging.getLogger(__name__)

class FactorModel:
    def __init__(self):
        self.factors = {}
        self.factor_returns = None
        self.factor_exposures = None
        
    def calculate_value_factors(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """计算价值因子"""
        try:
            pe = data['Close'] / data['EPS']
            pb = data['Close'] / data['BookValue']
            ps = data['Close'] / data['Sales']
            
            return {
                'PE': pe,
                'PB': pb,
                'PS': ps
            }
        except Exception as e:
            logger.error(f"计算价值因子失败: {str(e)}")
            return {}
            
    def calculate_momentum_factors(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """计算动量因子"""
        try:
            returns = data['Close'].pct_change()
            
            momentum_12m = returns.rolling(252).sum()  # 12个月动量
            momentum_6m = returns.rolling(126).sum()   # 6个月动量
            momentum_3m = returns.rolling(63).sum()    # 3个月动量
            
            return {
                'MOM_12M': momentum_12m,
                'MOM_6M': momentum_6m,
                'MOM_3M': momentum_3m
            }
        except Exception as e:
            logger.error(f"计算动量因子失败: {str(e)}")
            return {}
            
    def calculate_volatility_factors(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """计算波动率因子"""
        try:
            returns = data['Close'].pct_change()
            
            vol_annual = returns.rolling(252).std() * np.sqrt(252)
            vol_6m = returns.rolling(126).std() * np.sqrt(252)
            vol_3m = returns.rolling(63).std() * np.sqrt(252)
            
            return {
                'VOL_Annual': vol_annual,
                'VOL_6M': vol_6m,
                'VOL_3M': vol_3m
            }
        except Exception as e:
            logger.error(f"计算波动率因子失败: {str(e)}")
            return {}
            
    def calculate_quality_factors(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """计算质量因子"""
        try:
            roe = data['NetIncome'] / data['Equity']
            roa = data['NetIncome'] / data['Assets']
            gross_margin = data['GrossProfit'] / data['Revenue']
            
            return {
                'ROE': roe,
                'ROA': roa,
                'GrossMargin': gross_margin
            }
        except Exception as e:
            logger.error(f"计算质量因子失败: {str(e)}")
            return {}
            
    def estimate_factor_returns(self, returns: pd.Series, 
                              factor_exposures: pd.DataFrame) -> pd.Series:
        """估计因子收益率"""
        try:
            model = LinearRegression()
            model.fit(factor_exposures, returns)
            self.factor_returns = pd.Series(model.coef_, index=factor_exposures.columns)
            return self.factor_returns
        except Exception as e:
            logger.error(f"估计因子收益率失败: {str(e)}")
            return pd.Series() 