from dataclerk.task.DataClerkTaskExecutor import DataClerkTaskExecutor
from modules.kinetic_core.AbstractClient import rpc, lpc
from modules.kinetic_core.AbstractExecutor import executor
from modules.kinetic_core.AbstractMobileClient import AbstractMobileClient


@executor(DataClerkTaskExecutor)
class DataClerkTaskClient(AbstractMobileClient):

    @rpc
    async def add(self, supplier_id=None, url=None, key=None, filename=None):
        pass

    @lpc
    async def list(self):
        pass

    @lpc
    async def size(self):
        pass

    @lpc
    async def get_one(self):
        pass

    @lpc
    async def delete(self, task_id):
        pass

    @rpc
    async def complete(self, task_id=None):
        pass
