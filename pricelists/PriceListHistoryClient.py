#region import
from modules.kinetic_core.AbstractClient import AbstractClient, rpc, lpc
from modules.kinetic_core.AbstractExecutor import executor
from .PriceListHistoryExecutor import PriceListHistoryExecutor
#endregion

@executor(PriceListHistoryExecutor)
class PriceListHistoryClient(AbstractClient):

    @lpc
    async def add(self, price=None):
        pass