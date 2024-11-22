export const formatMetric = (value: number, precision: number = 2): string => {
  if (Math.abs(value) < 0.01) {
    return value.toExponential(precision);
  }
  return value.toFixed(precision);
}; 