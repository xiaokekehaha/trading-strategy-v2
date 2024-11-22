import { UseQueryResult } from 'react-query';

declare module 'react-query' {
  export interface QueryResult<TData = unknown> extends UseQueryResult<TData> {
    data: TData;
  }
} 