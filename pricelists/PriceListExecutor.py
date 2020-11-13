# region import
from modules.kinetic_core.AbstractExecutor import *
from .PriceListDB import PriceListDB
from modules.kinetic_core.Connector import db
from .PriceListHistoryClient import PriceListHistoryClient
# endregion


class PriceList2Executor(AbstractExecutor):

    seed_params = {
        "agent_id": None,
        "product_id": None,
        "cash100": None,
        "wire0": None,
        "wire25": None,
        "wire50": None,
        "wire100": None,
        "quantity": None,
        "expiry": None
    }

    def __init__(self, task):
        super().__init__(task)
        self.indexable = True
        self.searchable_fields = ["name"]

    async def add(self, supplier_id, prices, key, keep=False):

        supplier_row = {
            "products": {},
            "delivery_fixed": 30000,
            "delivery_percent": 0.2,
            "delivery_free_min_price": 20000,
            "load": 0.01,
            "discount": [
                {"from": 3000, "percent": 0.05},
                {"from": 4000, "percent": 0.06}
            ]
        }
        products = dict()
        db = PriceListDB()
        # todo clear elastic
        if not keep:
            await AbstractExecutor.es.delete_by_query(index='pricelist2executor-index', doc_type='item',
                                                      body={'query': {'term': {'supplier_id': supplier_id}}})
            await db.remove((int(supplier_id)), "supplier_id")
        price_history = PriceListHistoryClient()
        for price_row in prices:
            price_row["key"] = str(key)
            if type(price_row["n"]) is float:
                # empty name
                continue
            if type(price_row["e"]) is dict:
                continue
            await self.save_price(int(supplier_id), price_row)
            if price_row["product_id"] not in price_row:
                products[str(price_row["product_id"])] = list()
            products[str(price_row["product_id"])].append(price_row)

        supplier_row["products"] = products

        return True

    async def get_one(self, pricelist_id):
        prices = await db.list("select *, current_timestamp from pharmex_pricelists_history where key = $1 limit 100", (str(pricelist_id),))
        return prices

    async def get_details(self, price_list_id):
        return await db.query("select *, current_timestamp from pharmex_pricelists where price_list_id = $1", (price_list_id,))

    async def get_prices_for(self, ids=None):
        prices = await db.list("select *, current_timestamp from pharmex_pricelists where product_id = any($1::int[])", (ids,))
        suppliers = {}
        for price in prices:
            supplier_id = str(price["supplier_id"])
            if supplier_id not in suppliers:
                suppliers[supplier_id] = {}
            p = {}

            p["expiry"] = price["expiry"]
            p["supplier_id"] = price["supplier_id"]
            p["product_id"] = price["product_id"]
            p["quantity"] = price["quantity"]
            p["created"] = price["created"]
            if price["cash"] is not None and price["cash"] > 0:
                p["cash"] = price["cash"]
            if price["wire100"] is not None and price["wire100"] > 0:
                p["wire100"] = price["wire100"]
            if price["wire75"] is not None and price["wire75"] > 0:
                p["wire75"] = price["wire75"]
            if price["wire50"] is not None and price["wire50"] > 0:
                p["wire50"] = price["wire50"]
            if price["wire25"] is not None and price["wire25"] > 0:
                p["wire25"] = price["wire25"]
            suppliers[supplier_id][price["product_id"]] = p
        return suppliers

    async def save_price(self, supplier_id, price_row, delete=False):

        price_db = PriceListDB()

        price_history = PriceListHistoryClient()
        price = {}
        price["supplier_id"] = int(supplier_id)
        price["name"] = price_row["n"]
        price["manufacturer"] = str(price_row["m"])
        price["key"] = price_row["key"]
        price["product_id"] = price_row["product_id"]
        price["cash"] = price_row["price_cash"]
        if "price_wire100" in price_row:
            price["wire100"] = price_row["price_wire100"]
        if "price_wire75" in price_row:
            price["wire75"] = price_row["price_wire75"]
        if "wire50" in price_row:
            price["wire50"] = price_row["price_wire50"]
        if "wire25" in price_row:
            price["wire25"] = price_row["price_wire25"]
        price["quantity"] = price_row["quantity"]
        price["expiry"] = price_row["e"]
        try:

            price = await price_db.add(price)
        except:
            print('Failed inserting price')
            print(price)
            raise Exception("Failed inserting price")

        # MODIFICATIONS:
        await price_history.add(price=price)

        # adding to elastic
        await AbstractExecutor.es.index(index='pricelist2executor-index', doc_type='item',
                                        id=price["price_list_id"],
                                        body=json.dumps(price, cls=DateTimeEncoderCompact2))

    async def paginate(self, limit, offset):
        val = await db.list('select p.*,a.company_name, current_timestamp from pharmex_pricelists p left join pharmex_agents a on a.agent_id=p.supplier_id order by price_list_id desc limit $1 offset $2', (limit, offset))
        count = await db.query('select count(*) as count, current_timestamp from pharmex_pricelists')
        return {"count": count["count"], "data": val}

    async def list(self):
        return await self._list()

    async def get_all_db(self):
        return await db.list('select * from pharmex_pricelists')

    async def remove(self, product_id, agent_id):
        await db.query("delete from pharmex_pricelists where product_id=$1 and supplier_id=$2", (product_id, agent_id))
        return True

    async def modify(self, product_id, price_list_id):

        # TODO: modify
        #db = PriceListDB()
        # result = await db.persist(data={"product_id": product_id}, filter=product_id, key=price_list_id)
        # await self.save({str(filter): result})
        # await self.save({str(supplier_id): result})
        # return None

        db = PriceListDB()
        result = await db.db_modify(product_id=product_id, price_list_id=price_list_id)
        if result is not None:
            await AbstractExecutor.es.index(index='pricelist2executor-index', doc_type='item',
                                            id=result["price_list_id"],
                                            body=json.dumps(result, cls=DateTimeEncoderCompact2))

    # async def list_by_products(self, pids=None):
    #    price_list = await self._list()
    #    for s in price_list:
    #        for pid in pids:
    #            if pid in price_list:
    #
    #            r = prilist[s].get(pid, None)
    #            if r is not None:
    #                result[s] = r

    async def remove_pharmacy_product(self, product_id):
        db = PriceListDB()
        await db.remove_pharmacy_product(product_id=product_id)
