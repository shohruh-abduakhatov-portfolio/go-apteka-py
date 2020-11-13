from modules.kinetic_core.AbstractClient import AbstractClient, rpc, lpc
from modules.kinetic_core.AbstractExecutor import executor
from suppliers.SuppliersExportTemplateExecutor import SuppliersExportTemplateExecutor


@executor(SuppliersExportTemplateExecutor)
class SuppliersExportTemplateClient(AbstractClient):

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
    async def get_one(self, key=None):
        """
        Retrieve info about suppliers
        :return: dict containing (name, contact_phone, etc)
        """
        pass

    @rpc
    async def list(self):
        pass

