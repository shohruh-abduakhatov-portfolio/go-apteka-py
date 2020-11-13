from modules.kinetic_core.AbstractClient import AbstractClient, rpc, lpc
from modules.kinetic_core.AbstractExecutor import executor
from .AgentFullAliasesExecutor import AgentFullAliasesExecutor


@executor(AgentFullAliasesExecutor)
class AgentFullAliasesClient(AbstractClient):

    @rpc
    async def add(self, data=None):
        """
        Register suppliers within our system
        :return: supplier_id
        """
        pass

    @rpc
    async def modify(self, data=None, filter=None):
        """

        :param filter:
        :param data: dict containing suppliers name, phone, location, etc
        :return:
        """
        pass

    @lpc
    async def find(self, alias_product, alias_manufacturer):
        pass

    @lpc
    async def list_names(self):
        pass

    @lpc
    async def list(self, limit, offset):
        pass

    @lpc
    async def list_by_product_id(self, product_id):
        pass

    @lpc
    async def get_one(self, key=None):
        """
        Retrieve info about suppliers
        :return: dict containing (name, contact_phone, etc)
        """
        pass

    @lpc
    async def delete(self, alias_id):
        pass

    @rpc
    async def list(self):
        pass
