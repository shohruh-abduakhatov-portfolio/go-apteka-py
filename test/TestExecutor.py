from modules.kinetic_core.AbstractExecutor import AbstractExecutor
import asyncio

class TestExecutor(AbstractExecutor):
    
    async def heavy_operations(self):
        await asyncio.sleep(1*60)
        return True
