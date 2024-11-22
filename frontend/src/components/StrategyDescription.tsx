'use client';

import React from 'react';
import { STRATEGY_OPTIONS } from '@/types/strategy';

interface Props {
  strategy: string;
}

const STRATEGY_DESCRIPTIONS: Record<string, string> = {
  'bollinger_bands': '布林带策略是一种技术分析工具，使用移动平均线和标准差来生成上下轨道。当价格突破上轨时卖出，突破下轨时买入。',
  'macd': 'MACD策略使用两条不同周期的移动平均线之差来判断趋势。当MACD线与信号线交叉时产生买卖信号。',
  'moving_average': '移动平均策略使用两条不同周期的移动平均线。当短期均线上穿长期均线时买入（金叉），下穿时卖出（死叉）。',
  'svm': 'SVM策略使用支持向量机算法学习市场模式，通过历史数据训练模型来预测未来价格走势，适合处理非线性市场关系。',
  'random_forest': '随机森林策略综合多个决策树的预测结果，通过集成学习提高预测准确性，同时提供特征重要性分析。',
  'xgboost': 'XGBoost策略使用梯度提升树算法，通过迭代优化来提高预测准确性，特别适合处理复杂的市场数据。',
  'lstm': 'LSTM策略使用长短期记忆神经网络，能够捕捉市场的长期依赖关系，特别适合处理时间序列数据。',
  'mlp': 'MLP深度神经网络策略使用多层感知机进行市场模式识别，能够学习复杂的非线性关系。',
  'lstm_mlp': 'LSTM+MLP混合网络结合了LSTM的时序建模能力和MLP的特征提取能力，可以同时捕捉长期依赖和局部特征。',
  'cnn_mlp': 'CNN+MLP混合网络使用卷积神经网络提取局部特征模式，配合MLP进行分类预测，适合发现市场中的局部形态。'
};

const StrategyDescriptionComponent: React.FC<Props> = ({ strategy }) => {
  const strategyName = STRATEGY_OPTIONS[strategy] || strategy;
  const description = STRATEGY_DESCRIPTIONS[strategy] || '暂无策略描述';

  return (
    <div className="bg-white p-4 rounded-lg shadow mb-6">
      <h3 className="text-lg font-medium text-gray-900 mb-2">
        {strategyName}
      </h3>
      <p className="text-gray-600">
        {description}
      </p>
    </div>
  );
};

export default StrategyDescriptionComponent; 