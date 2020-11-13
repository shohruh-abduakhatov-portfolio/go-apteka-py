from modules.kinetic_core.AbstractDB import AbstractDB, table
from modules.kinetic_core.Connector import db


@table(name="pharmex_pricelists", key="price_list_id")
class PriceListDB(AbstractDB):
    pass

    async def db_modify(self, product_id, price_list_id):
        return await db.query("update pharmex_pricelists set product_id = $1 where price_list_id = $2 "
                              "returning price_list_id, supplier_id, product_id, cash, wire25, wire50, "
                              "wire75, wire100, quantity, expiry, name, manufacturer, key, created, current_timestamp", (product_id, price_list_id,))

    async def remove_pharmacy_product(self, product_id):
        await db.query("delete from pharmex_pricelists where product_id = $1 and supplier_id in (select agent_id from pharmex_agents where pharmacy=1)", (product_id,))
