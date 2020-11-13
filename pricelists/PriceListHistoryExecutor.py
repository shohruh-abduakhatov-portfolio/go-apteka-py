#region import 
from modules.kinetic_core.AbstractExecutor import AbstractExecutor
from .PriceListHistoryDB import PriceListHistoryDB
#endregion

class PriceListHistoryExecutor(AbstractExecutor):

    async def add(self, price):
        p = price.copy()
        db = PriceListHistoryDB()
        del p["price_list_id"]
        await db.add(p)
        return True