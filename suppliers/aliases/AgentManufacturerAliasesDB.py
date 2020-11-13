from modules.kinetic_core.AbstractDB import AbstractDB, table
from modules.kinetic_core.Connector import db

@table(name="suppliers_manufacturer_aliases", key="alias_id")
class AgentManufacturerAliasesDB(AbstractDB):

    async def list_by_manufacturer_id(self, manufacturer_id):
        return await db.list("select * from suppliers_manufacturer_aliases where manufacturer_id = $1",
        (manufacturer_id, ))

    async def get_all(self):
        return (await db.list('select a.*,m.name as origin, current_timestamp from suppliers_manufacturer_aliases a left join manufacturers m on m.manufacturer_id=a.manufacturer_id'))
