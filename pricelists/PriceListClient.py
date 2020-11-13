from modules.kinetic_core.AbstractClient import AbstractClient, rpc, lpc
from .PriceListExecutor import PriceList2Executor
from modules.kinetic_core.AbstractExecutor import executor


@executor(PriceList2Executor)
class PriceListClient(AbstractClient):

    @rpc
    async def add(self, supplier_id, prices, key, keep=False):
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
    async def get_one(self, pricelist_id):
        pass

    @lpc
    async def get_prices_for(self, ids=None):
        pass

    @lpc
    async def paginate(self, limit, offset):
        pass

    @lpc
    async def get_details(self, price_list_id):
        pass

    @rpc
    async def remove(self, product_id, agent_id):
        pass

    @lpc
    async def get_all_db(self):
        pass

    @rpc
    async def modify(self, product_id, price_list_id):
        pass

    @lpc
    async def save_price(self, supplier_id, price_row, delete=False):
        pass

    @lpc
    async def remove_pharmacy_product(self, product_id):
        pass


"""

86935	53	19589	0				20600	100	2021-07-01	Адипин таб. 5мг №30 GMP	гмп	1554358031.3999956	2019-04-25 07:14:03.665394


"""
