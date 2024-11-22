import React from 'react';

interface InputProps {
  label: string;
  value: string | number;
  onChange: (value: string) => void;
  type?: 'text' | 'number' | 'date' | 'checkbox';
  required?: boolean;
  min?: number;
  max?: number;
  step?: number;
}

export const Input: React.FC<InputProps> = ({
  label,
  value,
  onChange,
  type = 'text',
  required = false,
  min,
  max,
  step
}) => {
  return (
    <div className="space-y-1">
      <label className="block text-sm font-medium text-gray-700">
        {label}
      </label>
      <input
        type={type}
        value={value}
        checked={type === 'checkbox' ? Boolean(value) : undefined}
        onChange={(e) => onChange(type === 'checkbox' ? String(e.target.checked) : e.target.value)}
        required={required}
        min={min}
        max={max}
        step={step}
        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
      />
    </div>
  );
}; 