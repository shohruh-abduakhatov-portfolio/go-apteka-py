from modules.kinetic_core.AbstractDB import AbstractDB, table
from modules.kinetic_core.Connector import db

@table(name="suppliers_product_aliases", key="alias_id")
class AgentProductAliasesDB(AbstractDB):
    
    async def list_by_product_id(self, product_id):
        return await db.list("select * from suppliers_product_aliases where product_id = $1",
        (product_id, ))

    async def list(self):
        return await db.list("select a.product_id, LOWER(alias) as alias, name from suppliers_product_aliases a left join products p on a.product_id = p.product_id")

