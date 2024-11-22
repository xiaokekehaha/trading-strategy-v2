import React from 'react';
import { Button } from '../common/Button';

interface ChartControlsProps {
  onPeriodChange: (period: string) => void;
  onIndicatorToggle: (indicator: string) => void;
  selectedPeriod: string;
  activeIndicators: string[];
}

export const ChartControls: React.FC<ChartControlsProps> = ({
  onPeriodChange,
  onIndicatorToggle,
  selectedPeriod,
  activeIndicators
}) => {
  const periods = ['1D', '1W', '1M', '3M', '6M', '1Y', 'ALL'];
  const indicators = ['MA', 'MACD', 'RSI', 'BOLL'];

  return (
    <div className="flex flex-col space-y-4">
      <div className="flex space-x-2">
        {periods.map(period => (
          <Button
            key={period}
            variant={selectedPeriod === period ? 'primary' : 'secondary'}
            onClick={() => onPeriodChange(period)}
          >
            {period}
          </Button>
        ))}
      </div>
      
      <div className="flex space-x-2">
        {indicators.map(indicator => (
          <Button
            key={indicator}
            variant={activeIndicators.includes(indicator) ? 'primary' : 'secondary'}
            onClick={() => onIndicatorToggle(indicator)}
          >
            {indicator}
          </Button>
        ))}
      </div>
    </div>
  );
}; 