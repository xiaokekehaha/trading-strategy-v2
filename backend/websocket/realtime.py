from fastapi import WebSocket
from typing import Dict, List
import asyncio
import json
from ..services.market_data_service import MarketDataService

class RealtimeManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.market_data = MarketDataService()
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        
    async def broadcast(self, message: Dict):
        for connection in self.active_connections:
            await connection.send_json(message)
            
    async def start_streaming(self):
        while True:
            data = await self.market_data.get_realtime_data()
            await self.broadcast({
                "type": "market_data",
                "data": data
            })
            await asyncio.sleep(1)

realtime_manager = RealtimeManager()

async def websocket_endpoint(websocket: WebSocket):
    await realtime_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 处理接收到的消息
            await websocket.send_json({
                "status": "received",
                "data": json.loads(data)
            })
    except Exception as e:
        realtime_manager.disconnect(websocket) 