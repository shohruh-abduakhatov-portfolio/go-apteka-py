from .ManufacturerExecutor import ManufacturerExecutor
from modules.kinetic_core.AbstractClient import AbstractClient, rpc, lpc
from modules.kinetic_core.AbstractExecutor import executor


@executor(ManufacturerExecutor)
class ManufacturerClient(AbstractClient):

    @rpc
    async def add(self, name=None):
        pass

    @rpc
    async def modify(self, manufacturer=None, filter_by=None):
        pass

    @rpc
    async def remove(self, name):
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
    async def get_by_id(self, mid=None):
        pass

    @lpc
    async def get_by_name(self, name):
        pass

    @lpc
    async def best_matches(self, names):
        pass

