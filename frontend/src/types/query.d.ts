import { QueryClient } from '@tanstack/react-query';

declare module '@tanstack/react-query' {
  interface QueryClientConfig {
    defaultOptions?: {
      queries?: {
        staleTime?: number;
        refetchOnWindowFocus?: boolean;
      };
    };
  }
} 