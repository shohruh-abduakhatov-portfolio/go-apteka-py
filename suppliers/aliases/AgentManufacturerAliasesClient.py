from modules.kinetic_core.AbstractClient import AbstractClient, rpc, lpc
from modules.kinetic_core.AbstractExecutor import executor
from suppliers.aliases.AgentManufacturerAliasesExecutor import AgentManufacturerAliasesExecutor


@executor(AgentManufacturerAliasesExecutor)
class AgentManufacturerAliasesClient(AbstractClient):

    @rpc
    async def add(self, manufacturer_id=None, alias=None, agent_id=None):
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
    async def get_one(self, key=None):
        """
        Retrieve info about suppliers
        :return: dict containing (name, contact_phone, etc)
        """
        pass

    @lpc
    async def list(self):
        pass

    @lpc
    async def list_by_manufacturer_id(self, manufacturer_id=None):
        pass

    @lpc
    async def list_names(self, agent_id):
        pass

    @lpc
    async def matches(self, names):
        pass

    @lpc
    async def get_all(self):
        pass

    @lpc
    async def remove(self, alias_id):
        pass

