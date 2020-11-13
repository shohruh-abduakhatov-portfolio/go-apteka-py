from fuzzywuzzy import fuzz

from .NewProductTaskDB import NewProductTaskDB
from modules.kinetic_core.AbstractExecutor import AbstractExecutor
from modules.kinetic_core.Connector import db as raw_db


class NewProductTaskExecutor(AbstractExecutor):
    params = {
        "task_id": None,
        "name": None,
        "manufacturer": None,
        "type": None,
        "supplier_id": None,
        "created": None
    }

    def __init__(self, task):
        super().__init__(task)
        self.uid = "task_id"

    async def add(self, task):
        q = await raw_db.query("select task_id, current_timestamp from new_product_tasks where name = $1 and manufacturer = $2", (task["name"], task["manufacturer"]))
        if q is None:
            db = NewProductTaskDB()
            result = await db.add(task)
            instance_id = result[self.uid]
            task[self.uid] = instance_id
            return {self.uid: instance_id}
        else:
            return {self.uid: q["task_id"]}

    async def modify(self, task, filter_by):
        db = NewProductTaskDB()
        result = await db.persist(task, filter_by)
        return True

    async def remove(self, task_id):
        manufacturer = await self.get([str(task_id)])
        if manufacturer is None:
            return False
        db = NewProductTaskDB()
        result = await db.remove({"task_id": task_id}, key="task_id")
        return True

    async def list(self):
        db = NewProductTaskDB()
        return await db.get_all()

    async def paginate(self, limit, offset):
        db = NewProductTaskDB()
        instances = await db.paginate(limit, offset)
        return instances

    async def get_one(self, key):
        return await self.get([key])

    async def get_uncompleted(self, offset, supplier_id):
        db = NewProductTaskDB()
        return await db.get_uncompleted(offset, supplier_id)

    async def group_tasks(self):
        db = NewProductTaskDB()
        return await db.group_tasks()
