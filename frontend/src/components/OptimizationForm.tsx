import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import DatePicker from 'react-datepicker';
import type { StrategyConfig, BaseStrategyParams } from '@/types/strategy';
import "react-datepicker/dist/react-datepicker.css";

interface FormData {
  symbols: string[];
  startDate: Date;
  endDate: Date;
  strategies: StrategyConfig[];
}

interface OptimizationFormProps {
  onSubmit: (data: FormData) => void;
  availableStrategies: string[];
}

export const OptimizationForm: React.FC<OptimizationFormProps> = ({
  onSubmit,
  availableStrategies
}) => {
  const { control, handleSubmit } = useForm<FormData>();
  const [strategies, setStrategies] = useState<StrategyConfig[]>([]);

  const handleAddStrategy = () => {
    setStrategies([
      ...strategies,
      {
        name: availableStrategies[0],
        params: {}
      }
    ]);
  };

  const handleRemoveStrategy = (index: number) => {
    setStrategies(strategies.filter((_, i) => i !== index));
  };

  const handleStrategyParamChange = (index: number, params: BaseStrategyParams) => {
    const newStrategies = [...strategies];
    newStrategies[index].params = params;
    setStrategies(newStrategies);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700">
          股票代码 (用逗号分隔)
        </label>
        <Controller
          name="symbols"
          control={control}
          defaultValue={[]}
          render={({ field: { onChange, value } }) => (
            <input
              type="text"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
              onChange={(e) => onChange(e.target.value.split(','))}
              value={value?.join(',') || ''}
            />
          )}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            开始日期
          </label>
          <Controller
            name="startDate"
            control={control}
            render={({ field: { onChange, value } }) => (
              <DatePicker
                selected={value}
                onChange={onChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
              />
            )}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">
            结束日期
          </label>
          <Controller
            name="endDate"
            control={control}
            render={({ field: { onChange, value } }) => (
              <DatePicker
                selected={value}
                onChange={onChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
              />
            )}
          />
        </div>
      </div>

      <div>
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-medium">策略配置</h3>
          <button
            type="button"
            onClick={handleAddStrategy}
            className="px-4 py-2 bg-blue-500 text-white rounded-md"
          >
            添加策略
          </button>
        </div>
        
        {strategies.map((strategy, index) => (
          <div key={index} className="mt-4 p-4 border rounded-md">
            <div className="flex justify-between">
              <Controller
                name={`strategies.${index}.name`}
                control={control}
                defaultValue={strategy.name}
                render={({ field: { onChange, value } }) => (
                  <select
                    value={value}
                    onChange={onChange}
                    className="block w-full rounded-md border-gray-300"
                  >
                    {availableStrategies.map(name => (
                      <option key={name} value={name}>
                        {name}
                      </option>
                    ))}
                  </select>
                )}
              />
              <button
                type="button"
                onClick={() => handleRemoveStrategy(index)}
                className="ml-2 text-red-500"
              >
                删除
              </button>
            </div>
            
            <StrategyParams
              strategy={strategy}
              onChange={(params) => handleStrategyParamChange(index, params)}
            />
          </div>
        ))}
      </div>

      <button
        type="submit"
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-md"
      >
        开始优化
      </button>
    </form>
  );
};

interface StrategyParamsProps {
  strategy: StrategyConfig;
  onChange: (params: BaseStrategyParams) => void;
}

const StrategyParams: React.FC<StrategyParamsProps> = ({ strategy, onChange }) => {
  const handleParamChange = (key: keyof BaseStrategyParams, value: number) => {
    onChange({
      ...strategy.params,
      [key]: value
    });
  };

  // 根据策略类型显示不同的参数配置
  switch (strategy.name) {
    case 'bollinger_bands':
      return (
        <div className="mt-4 grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              窗口期
            </label>
            <input
              type="number"
              value={strategy.params.window || 20}
              onChange={(e) => handleParamChange('window', +e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              标准差倍数
            </label>
            <input
              type="number"
              value={strategy.params.num_std || 2}
              onChange={(e) => handleParamChange('num_std', +e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            />
          </div>
        </div>
      );
    // 添加其他策略的参数配置...
    default:
      return null;
  }
}; 