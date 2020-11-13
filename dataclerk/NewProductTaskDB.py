from modules.kinetic_core.AbstractDB import AbstractDB, table
from modules.kinetic_core.Connector import db


@table(name="new_product_tasks", key="task_id")
class NewProductTaskDB(AbstractDB):

    async def paginate(self, limit, offset):
        val = await db.list("select *, current_timestamp from new_product_tasks order by name limit $1 offset $2", (limit, offset))
        count = await db.query("select count(1) as count,current_timestamp from new_product_tasks")
        return {"count": count["count"], "data": val}

    async def get_all(self):
        return (await db.list('select *, current_timestamp from new_product_tasks'))

    async def get_uncompleted(self, offset, supplier_id):
        return (await db.list('select *, current_timestamp from new_product_tasks  where completed is null and supplier_id=$1 order by task_id desc limit 50 offset $2', (supplier_id, offset,)))

    async def group_tasks(self):
        return await db.list("select tasks, supplier_id, company_name from (select count(*) as tasks, supplier_id from new_product_tasks group by supplier_id) as t left join pharmex_agents on pharmex_agents.agent_id = t.supplier_id")
