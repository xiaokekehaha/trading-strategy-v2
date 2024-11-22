import { useState } from 'react'
import { useBacktest } from '@/hooks/useBacktest'
import { Button } from '../common/Button'
import { Input } from '../common/Input'
import type { BacktestParams } from '@/types/backtest'

export const BacktestForm = () => {
  const [params, setParams] = useState<BacktestParams>({
    symbol: '',
    startDate: '',
    endDate: '',
    strategy: {
      name: '',
      params: {}
    },
    initial_capital: 100000
  })
  
  const { runBacktest, isLoading } = useBacktest()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await runBacktest(params)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="股票代码"
        value={params.symbol}
        onChange={(value) => setParams(prev => ({
          ...prev,
          symbol: value
        }))}
      />
      
      <Input
        label="开始日期"
        type="date"
        value={params.startDate}
        onChange={(value) => setParams(prev => ({
          ...prev,
          startDate: value
        }))}
      />

      <Input
        label="结束日期" 
        type="date"
        value={params.endDate}
        onChange={(value) => setParams(prev => ({
          ...prev,
          endDate: value
        }))}
      />

      <Input
        label="初始资金"
        type="number"
        value={String(params.initial_capital)}
        onChange={(value) => setParams(prev => ({
          ...prev,
          initial_capital: Number(value)
        }))}
      />

      <Button 
        type="submit"
        disabled={isLoading}
      >
        {isLoading ? '回测中...' : '开始回测'}
      </Button>
    </form>
  )
} 