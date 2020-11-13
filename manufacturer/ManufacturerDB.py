from modules.kinetic_core.AbstractDB import AbstractDB, table
from modules.kinetic_core.Connector import db

@table(name="manufacturers", key="manufacturer_id")
class ManufacturerDB(AbstractDB):
    
    async def paginate(self, limit, offset):
        val = await db.list("select manufacturer_id, name, country, current_timestamp from manufacturers order by name limit $1 offset $2", (limit, offset))
        count = await db.query("select count(1) as count,current_timestamp from manufacturers")
        return {"count": count["count"], "data": val}

    async def get_all(self):
        return (await db.list('select *, current_timestamp from manufacturers'))
