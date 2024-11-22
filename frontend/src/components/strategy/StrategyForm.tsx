import { useState } from 'react'
import { useStrategy } from '@/hooks/useStrategy'
import { Button } from '../common/Button'
import { Input } from '../common/Input'
import { Select } from '../common/Select'
import type { Strategy, StrategyConfig, BaseStrategyParams } from '@/types/strategy'

export const StrategyForm = () => {
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy>()
  const [params, setParams] = useState<BaseStrategyParams>({})
  const { strategies, createStrategy } = useStrategy()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedStrategy) return
    
    await createStrategy({
      name: selectedStrategy.name,
      params
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Select
        label="选择策略"
        value={selectedStrategy?.name || ''}
        onChange={(value) => setSelectedStrategy(
          strategies.find(s => s.name === value)
        )}
        options={strategies.map(s => ({
          label: s.name,
          value: s.name
        }))}
      />

      {selectedStrategy?.params.map(param => (
        <Input
          key={param.name}
          label={param.label}
          type={param.type === 'boolean' ? 'checkbox' : 'number'}
          value={String(params[param.name] || '')}
          onChange={(value) => setParams(prev => ({
            ...prev,
            [param.name]: param.type === 'boolean' ? Boolean(value) : Number(value)
          }))}
        />
      ))}

      <Button type="submit">
        创建策略
      </Button>
    </form>
  )
} 