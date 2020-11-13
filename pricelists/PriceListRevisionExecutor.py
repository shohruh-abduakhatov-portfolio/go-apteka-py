from modules.kinetic_core.AbstractExecutor import AbstractExecutor
from .PriceListRevisionDB import PriceListRevisionDB


class PriceListRevisionExecutor(AbstractExecutor):
    params = {
        "revision_id": None,
        "agent_id": None,
        "key": None,
        "name_column": None,
        "manufacturer_column": -1,
        "price_cash_column": -1,
        "price_wire100_column": -1,
        "price_wire75_column": -1,
        "price_wire50_column": -1,
        "price_wire25_column": -1,
        "price_wire100_percent": -1,
        "price_wire75_percent": -1,
        "price_wire50_percent": -1,
        "price_wire25_percent": -1,
        "expiry_column": None,
        "count": 0,
        "row_offset": None,
        "ignore": None,
        "manual_ignore": None
    }

    def __init__(self, task):
        super().__init__(task)
        self.uid = "key"

    async def add(self, revision):
        for d in revision:
            self.params[d] = revision[d]
        db = PriceListRevisionDB()

        supplier_id = revision["agent_id"]
        result = await db.add(revision)
        await self.save({str(revision["key"]): self.params})
        return {self.uid: revision["key"]}

    async def upsert(self, revision):
        key = revision["key"]
        has = await self.get_one(key=key)
        if has is not None:
            await self.modify(data=revision, filter=key)
            return has
        else:
            return await self.add(revision=revision)

    async def modify(self, data, filter):
        db = PriceListRevisionDB()
        result = await db.persist(data, filter)
        await self.save({str(filter): result})
        return None

    async def publish_pricelist(self, key, count):
        pricelist = await self.get_one(key=key)

        await self.deactivate(supplier_id=pricelist["agent_id"], key=str(key))
        await self.modify(data={"completed": 1, "count": count}, filter=str(key))
        await self.save({str(key): None})
        from dataclerk.task.DataClerkTaskClient import DataClerkTaskClient
        task_executor = DataClerkTaskClient()
        await task_executor.complete(task_id=key)
        return None

    async def deactivate(self, supplier_id, key):
        from modules.kinetic_core.Connector import db
        revision = await db.query("update pharmex_pricelist_revision set deactivated_at = current_timestamp where deactivated_at is null and agent_id=$1 and key != $2 returning revision_id, current_timestamp", (supplier_id, key))
        return True

    async def is_manual(self, key, manual):
        await self.modify(data={"manual": 1 if manual else 0}, filter=key)

    async def get_one(self, key):
        from modules.kinetic_core.Connector import db
        return await db.query("select *, current_timestamp from pharmex_pricelist_revision where key=$1", (key,))

    async def list_active(self, limit, offset):
        from modules.kinetic_core.Connector import db
        val = await db.list("select r.*, a.company_name as name from pharmex_pricelist_revision as r left join pharmex_agents as a on a.agent_id = r.agent_id where completed=1 and deactivated_at is null order by revision_id desc limit $1 offset $2", (limit, offset))
        count = await db.query("select count(1) as count,current_timestamp from pharmex_pricelist_revision where completed=1 and deactivated_at is null")
        return {"count": count["count"], "data": val}

    async def list(self, limit, offset):
        from modules.kinetic_core.Connector import db
        val = await db.list("select r.*, a.company_name as name from pharmex_pricelist_revision as r left join pharmex_agents as a on a.agent_id = r.agent_id where completed=1 order by revision_id desc limit $1 offset $2", (limit, offset))
        return val

    async def get_by_agent(self, agent_id):
        from modules.kinetic_core.Connector import db
        return await db.query("select *, current_timestamp from pharmex_pricelist_revision where deactivated_at is null and completed = 1 and agent_id = $1", (agent_id,))
