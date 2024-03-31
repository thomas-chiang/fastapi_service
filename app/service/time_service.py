import asyncio
import time

def get_current_timestamp() -> int:
    return round(time.time())

class TimeService:
    timestamp_interval = 60 * 60 * 24  # seconds of one day
        
    async def get_current_timestamp(self) -> int:
        return await asyncio.to_thread(get_current_timestamp)
    
    async def get_previous_day_timestamp(self) -> int:
        return await self.get_current_timestamp() - self.timestamp_interval
