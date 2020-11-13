# region import
from modules.kinetic_core.AbstractClient import AbstractClient, rpc, lpc
from .PriceListRevisionExecutor import PriceListRevisionExecutor
from modules.kinetic_core.AbstractExecutor import executor
# endregion


@executor(PriceListRevisionExecutor)
class PriceListRevisionClient(AbstractClient):

    @rpc
    async def add(self, revision):
        """

        :param data: dict which contains {
            "export_template_id": None,
            "supplier_id": None,
            "name_column": None,
            "manufacturer_column": None,
            "price_cash_column": None,
            "price_cashless_column": None,
            "expiry_column": None,
            "row_offset": None,
            "date_mask": None
        }
        :return:
        """
        pass

    @lpc
    async def is_manual(self, key, manual):
        pass

    @lpc
    async def get_one(self, key):
        pass

    @lpc
    async def get_by_agent(self, agent_id):
        pass

    @lpc
    async def list(self, limit, offset):
        pass

    @lpc
    async def list_active(self, limit, offset):
        pass

    @lpc
    async def upsert(self, revision):
        pass

    @rpc
    async def modify(self, data, filter):
        pass

    @rpc
    async def publish_pricelist(self, key, count):
        pass
