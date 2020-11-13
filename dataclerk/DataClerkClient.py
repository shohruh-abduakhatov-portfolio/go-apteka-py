from dataclerk.DataClerkExecutor import DataClerkExecutor
from modules.kinetic_core.AbstractClient import AbstractClient, rpc, lpc
from modules.kinetic_core.AbstractExecutor import executor


@executor(DataClerkExecutor)
class DataClerkClient(AbstractClient):

    @rpc
    async def upload(self, dictionary):
        pass

    @lpc
    async def get_one(self, key):
        pass

    @lpc
    async def remove(self, key):
        pass

    @rpc
    async def parse_pricelist(self, supplier, key):
        pass

    @rpc
    async def filter(self, revision):
        pass
