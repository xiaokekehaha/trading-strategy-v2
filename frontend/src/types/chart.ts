export interface ChartConfig {
  showVolume: boolean;
  showGrid: boolean;
  showTooltip: boolean;
  showCrosshair: boolean;
  chartType: 'candles' | 'line' | 'area';
  timeframe: Timeframe;
} 