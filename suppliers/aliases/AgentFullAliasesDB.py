from modules.kinetic_core.AbstractDB import AbstractDB, table
from modules.kinetic_core.Connector import db


@table(name="suppliers_full_aliases", key="alias_id")
class AgentFullAliasesDB(AbstractDB):

    async def list_by_product_id(self, product_id):
        return await db.list("select * from suppliers_full_aliases where product_id = $1",
                             (product_id, ))

    async def list(self):
        return await db.list("select a.product_id, LOWER(alias) as alias, name from suppliers_full_aliases a left join products p on a.product_id = p.product_id")

    async def find(self, alias_product, alias_manufacturer):
        return await db.query("select *, current_timestamp from suppliers_full_aliases where alias_product = $1 and alias_manufacturer = $2", (alias_product, alias_manufacturer))
