from typing import Dict, List, Optional
import asyncpg
from datetime import datetime

class DatabaseService:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None
        
    async def connect(self):
        """创建数据库连接池"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(self.dsn)
            
    async def close(self):
        """关闭数据库连接池"""
        if self.pool:
            await self.pool.close()
            
    async def save_backtest_result(
        self,
        strategy_name: str,
        params: Dict,
        results: Dict
    ) -> str:
        """保存回测结果"""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                """
                INSERT INTO backtest_results 
                (strategy_name, parameters, results, created_at)
                VALUES ($1, $2, $3, $4)
                RETURNING id
                """,
                strategy_name,
                params,
                results,
                datetime.now()
            )
            
    async def get_backtest_result(self, backtest_id: str) -> Optional[Dict]:
        """获取回测结果"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                """
                SELECT * FROM backtest_results 
                WHERE id = $1
                """,
                backtest_id
            )
            
    async def get_backtest_history(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict]:
        """获取回测历史"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT * FROM backtest_results 
                ORDER BY created_at DESC
                LIMIT $1 OFFSET $2
                """,
                limit,
                offset
            ) 