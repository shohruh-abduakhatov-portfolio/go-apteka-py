from .NewProductTaskExecutor import NewProductTaskExecutor
from modules.kinetic_core.AbstractClient import AbstractClient, lpc, lpc
from modules.kinetic_core.AbstractExecutor import executor


@executor(NewProductTaskExecutor)
class NewProductTaskClient(AbstractClient):

    @lpc
    async def add(self, task=None):
        pass

    @lpc
    async def modify(self, task=None, filter_by=None):
        pass

    @lpc
    async def remove(self, task_id):
        pass

    @lpc
    async def list(self):
        pass

    @lpc
    async def paginate(self, limit, offset):
        pass

    @lpc
    async def get_one(self, name):
        pass

    @lpc
    async def group_tasks(self):
        pass

    @lpc
    async def get_uncompleted(self, offset, supplier_id):
        pass
