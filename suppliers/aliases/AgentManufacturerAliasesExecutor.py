from manufacturer.ManufacturerClient import ManufacturerClient
from modules.kinetic_core.AbstractExecutor import *
from suppliers.aliases.AgentManufacturerAliasesDB import AgentManufacturerAliasesDB
from modules.business.warehouse.manufacturer.ManufacturerClient import ManufacturerClient


class AgentManufacturerAliasesExecutor(AbstractExecutor):
    params = {
        "alias_id": None,
        "agent_id": None,
        "manufacturer_id": None,
        "alias": None
    }

    def __init__(self, task):
        super().__init__(task)
        self.uid = "alias_id"
        self.indexable = True

    async def add(self, manufacturer_id=None, alias=None, agent_id=None):
        data = {"manufacturer_id": manufacturer_id,
                "alias": alias.lower(),
                "agent_id": agent_id}
        manufacturer_client = ManufacturerClient()
        manufacturer = await manufacturer_client.get_by_id(mid=manufacturer_id)
        data["origin"] = manufacturer["name"]
        db = AgentManufacturerAliasesDB()
        result = await db.add(data)
        instance_id = result[self.uid]
        data[self.uid] = instance_id
        await self.save({str(instance_id): data})
        return {self.uid: instance_id}

    async def modify(self, data, filter):
        params = await self.get([str(filter)])
        for d in data:
            self.params[d] = data[d]
        db = AgentManufacturerAliasesDB()
        result = await db.persist(data, filter)
        await self.save({str(filter): result})
        return True

    async def remove(self, alias_id):
        db = AgentManufacturerAliasesDB()
        await db.remove(alias_id, "alias_id")
        await self.save({str(alias_id): None})
        return True

    async def get_one(self, key):
        return await self.get([key])

    async def list_names(self, agent_id):
        aliases = await self._list()
        manufacturer_client = ManufacturerClient()
        result = dict()
        for aid, alias in aliases.items():
            if alias["agent_id"] == agent_id:
                origin = await manufacturer_client.get_by_id(mid=alias["manufacturer_id"])
                aliases[aid]["origin"] = origin["name"].lower()
                result[alias["alias"].lower()] = alias
        return result

    async def list(self):
        from modules.kinetic_core.Connector import db
        val = await db.list("select * from demand limit 10")
        return val

    async def get_all(self):
        db = AgentManufacturerAliasesDB()
        instances = await db.get_all()
        output = {}
        for i in instances:
            output[str(i["alias_id"])] = i
        return output

    async def matches(self, names):
        res = await AbstractExecutor.es.search(index="agentmanufactureraliasesexecutor-index", body={
            "query": {
                "constant_score": {
                    "filter": {
                        "terms": {
                            "alias.keyword": names
                        }
                    }
                },

            }, "from": 0, "size": 10000
        })
        manufacturers = {}
        for manufacturer in res["hits"]["hits"]:
            manufacturers[manufacturer["_source"]
                          ["alias"]] = manufacturer["_source"]
        return manufacturers

    async def list_by_manufacturer_id(self, manufacturer_id=None):
        db = AgentManufacturerAliasesDB()
        return await db.list_by_manufacturer_id(manufacturer_id)
