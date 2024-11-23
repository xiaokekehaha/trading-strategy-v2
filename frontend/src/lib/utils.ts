export const formatMetric = (value: number, precision: number = 2): string => {
  if (Math.abs(value) < 0.01) {
    return value.toExponential(precision);
  }
  return value.toFixed(precision);
};

export const formatPercentage = (value: number): string => {
  return `${(value * 100).toFixed(2)}%`;
};

export const formatRatio = (value: number): string => {
  return value.toFixed(2);
};

export const formatMoney = (value: number): string => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY'
  }).format(value);
};

export const formatDate = (date: string): string => {
  return new Date(date).toLocaleDateString('zh-CN');
};

export const formatNumber = (value: number): string => {
  return new Intl.NumberFormat('zh-CN').format(value);
};