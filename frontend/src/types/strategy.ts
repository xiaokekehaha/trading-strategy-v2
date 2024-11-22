export const STRATEGY_OPTIONS: Record<string, string> = {
  'bollinger_bands': '布林带策略',
  'macd': 'MACD策略',
  'moving_average': '移动平均策略',
  'svm': 'SVM策略',
  'random_forest': '随机森林策略',
  'xgboost': 'XGBoost策略',
  'lstm': 'LSTM策略'
};

export type Strategy = keyof typeof STRATEGY_OPTIONS; 