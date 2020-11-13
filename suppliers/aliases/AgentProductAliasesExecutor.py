from modules.kinetic_core.AbstractExecutor import AbstractExecutor
from modules.business.warehouse.ProductsExecutorClient import ProductsExecutorClient
from suppliers.aliases.AgentManufacturerAliasesDB import AgentManufacturerAliasesDB
from .AgentProductAliasesDB import AgentProductAliasesDB

class AgentProductAliasesExecutor(AbstractExecutor):
    params = {
        "alias_id": None,
        "agent_id": None,
        "product_id": None,
        "alias": None
    }

    def __init__(self, task):
        super().__init__(task)
        self.indexable = True
        self.uid = "alias_id"

    async def add(self, data):
        for d in data:
            self.params[d] = data[d]
        db = AgentProductAliasesDB()
        result = await db.add(data)
        instance_id = result[self.uid]
        self.params[self.uid] = instance_id
        await self.save({str(instance_id): self.params})
        return {self.uid: instance_id}

    async def modify(self, data, filter):
        params = await self.get([str(filter)])
        for d in data:
            self.params[d] = data[d]
        db = AgentProductAliasesDB()
        result = await db.persist(self.params, filter)
        await self.save({str(filter): result})
        return None

    async def get_one(self, key):
        return await self.get([key])

    async def list_by_product_id(self, product_id):
        db = AgentProductAliasesDB()
        return await db.list_by_product_id(product_id)

    async def list_names(self):
        db = AgentProductAliasesDB()
        aliases = await db.list()
        product_client = ProductsExecutorClient()
        result = dict()
        for alias in aliases:
            try:
                result[alias["alias"].lower()] = alias["name"]
            except Exception as identifier:
                traceback.print_exc()
                pass
        return result

    async def delete(self, alias_id=None):
        db = AgentProductAliasesDB()
        await db.remove(data=alias_id)
        await self.save({str(alias_id): None})

    async def list(self, limit, offset):
        from modules.kinetic_core.Connector import db
        val = await db.list(
            "select a.*, p.name, p.manufacturer, current_timestamp from suppliers_product_aliases a "
            " left join products p on p.product_id = a.product_id order by a.alias_id desc limit $1 offset $2",
            (limit, offset)
            )
        count = await db.query("select count(1), current_timestamp from suppliers_product_aliases")
        return {"count": count["count"], "data": val}
