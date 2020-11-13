from modules.kinetic_core.AbstractClient import AbstractClient, rpc, lpc
from modules.kinetic_core.AbstractExecutor import executor
from .SellerExecutor import SellerExecutor


@executor(SellerExecutor)
class SellerClient(AbstractClient):

    @lpc
    async def add(self, agent_id=None, telegram_id=None, name=None):
        pass

    @rpc
    async def find_by_telegram_id(self, telegram_id):
        pass

