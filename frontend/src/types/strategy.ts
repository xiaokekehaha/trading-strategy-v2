export const STRATEGY_OPTIONS = {
  'bollinger_bands': '布林带策略',
  'macd': 'MACD策略',
  'moving_average': '移动平均策略',
  'svm': 'SVM策略',
  'random_forest': '随机森林策略',
  'xgboost': 'XGBoost策略',
  'lstm': 'LSTM策略',
  'mlp': 'MLP深度神经网络',
  'lstm_mlp': 'LSTM+MLP混合网络',
  'cnn_mlp': 'CNN+MLP混合网络'
} as const;

export type Strategy = keyof typeof STRATEGY_OPTIONS; 