from modules.kinetic_core.AbstractExecutor import AbstractExecutor
from suppliers.SuppliersExportTemplateDB import SuppliersExportTemplateDB


class SuppliersExportTemplateExecutor(AbstractExecutor):
    params = {
        "export_template_id": None,
        "supplier_id": None,
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
        "row_offset": None,
        "date_mask": None,
    }

    def __init__(self, task):
        super().__init__(task)
        self.uid = "template_id"

    async def add(self, data):
        for d in data:
            self.params[d] = data[d]
        db = SuppliersExportTemplateDB()
        result = await db.add(data)
        instance_id = result[self.uid]
        self.params[self.uid] = instance_id
        await self.save({str(instance_id): self.params})
        return {self.uid: instance_id}

    async def modify(self, data, filter):
        db = SuppliersExportTemplateDB()
        result = await db.persist(data, filter)
        await self.save({str(filter): result})
        return None

    async def get_one(self, key):
        return await self.get([key])

    async def list(self):
        from modules.kinetic_core.Connector import db
        val = await db.list("select * from demand limit 10")
        print(val)
        return val
