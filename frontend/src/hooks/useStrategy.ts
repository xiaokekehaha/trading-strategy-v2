import { useQuery, useMutation } from '@tanstack/react-query';
import { getStrategies, createStrategy } from '@/services/api';
import type { Strategy, StrategyConfig } from '@/types/strategy';

export const useStrategy = () => {
  const { data: strategies = [] } = useQuery<Strategy[]>('strategies', getStrategies);

  const { mutate: create, isLoading } = useMutation<Strategy, Error, StrategyConfig>(
    createStrategy
  );

  return {
    strategies,
    createStrategy: create,
    isLoading
  };
}; 