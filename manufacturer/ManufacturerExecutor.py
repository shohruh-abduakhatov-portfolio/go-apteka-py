from fuzzywuzzy import fuzz

from manufacturer.ManufacturerDB import ManufacturerDB
from modules.kinetic_core.AbstractExecutor import AbstractExecutor


class ManufacturerExecutor(AbstractExecutor):
    params = {
        "manufacturer_id": None,
        "name": None,
        "country": None
    }

    def __init__(self, task):
        super().__init__(task)
        self.uid = "manufacturer_id"

    async def add(self, name=None):
        manufacturer = {"name": name.lower()}
        exists = await self.get_by_name(name)
        if exists is not None:
            print("exists")
            return {self.uid: exists[self.uid]}
        db = ManufacturerDB()
        result = await db.add(manufacturer)
        instance_id = result[self.uid]
        manufacturer[self.uid] = instance_id
        await self.save({"m" + manufacturer["name"]: manufacturer})
        await self.save({"i" + str(instance_id): manufacturer})
        return {self.uid: instance_id}

    async def modify(self, manufacturer, filter_by):
        db = ManufacturerDB()
        result = await db.persist(manufacturer, filter_by)
        await self.save({str(filter): result})
        return True

    async def remove(self, name):
        manufacturer = await self.get(["m" + name])
        if manufacturer is None:
            return False
        db = ManufacturerDB()
        result = await db.remove({"name": name}, key="name")
        await self.save({"m" + name: result})
        await self.save({"i" + str(manufacturer[self.uid]): result})
        return True

    async def list(self):
        return await self._list(prefix="i")

    async def paginate(self, limit, offset):
        db = ManufacturerDB()
        instances = await db.paginate(limit, offset)
        return instances

    async def get_one(self, key):
        return await self.get([key])

    async def get_by_id(self, mid):
        return await self.get(["i" + str(mid)])

    async def get_by_name(self, name):
        return await self.get(["m" + name])

    async def best_matches(self, names):
        instances = await self._list(prefix="m")
        result = {}
        for name in names:
            name = name.lower()
            matches = {}

            for instance in instances:
                i = instances[instance]
                if "name" in i:
                    n = i["name"].lower()
                    if len(instances[instance]) > 1:
                        ratio = fuzz.partial_ratio(name, n)
                        if ratio > 80:
                            matches[n] = {"ratio": ratio,
                                          "manufacturer_id": i[self.uid]}
            sorted_matches = sorted(
                matches.items(), key=lambda kv: -kv[1]["ratio"] * len(kv[0]))[:10]
            if len(sorted_matches) > 0:
                result[name] = sorted_matches
        return result
