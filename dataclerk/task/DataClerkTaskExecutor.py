from dataclerk.task.DataClerkTaskDB import DataClerkTaskDB
from dataclerk.DataClerkClient import DataClerkClient
from modules.kinetic_core.AbstractMobileExecutor import AbstractMobileExecutor

from pricelists.PriceListClient import PriceListClient
from pricelists.PriceListRevisionClient import PriceListRevisionClient

from collections import OrderedDict
import pandas as pandas


class DataClerkTaskExecutor(AbstractMobileExecutor):

    def __init__(self, task, webSocketConnector=None):
        super().__init__(task, webSocketConnector)
        self.uid = "task_id"

    async def add(self, supplier_id=None, url=None, key=None, filename=None):
        dataclerk = DataClerkClient()
        price_client = PriceListClient()
        revision_client = PriceListRevisionClient()
        # parse excel
        xls = pandas.ExcelFile(url)
        df = None
        sheets = xls.book.sheets()
        for sheet in sheets:
            if sheet.visibility == 0:
                df = pandas.read_excel(xls, sheet_name=sheet.name, header=None)

                if len(df) > 0:
                    break
        # df = pandas.read_excel(url, header=None)
        df = df.applymap(lambda x: x.strip() if type(x) is str else x)
        df = df.replace('  ', ' ', regex=True)
        # save file content to the redis
        save_to_redis = df.to_dict(orient='list', into=OrderedDict)
        print("upload")
        key_data = await dataclerk.upload(dictionary=save_to_redis)
        # trying to parse content automatically
        revision_key = key_data["key"]
        result = await dataclerk.parse_pricelist(supplier=supplier_id, key=revision_key)
        print("parse")
        revision = result["revision"]
        revision["key"] = revision_key
        revision["agent_id"] = supplier_id
        current_revision = await revision_client.upsert(revision=revision)
        # register revision
        print("upsert")
        revision = await revision_client.get_one(key=revision_key)
        # data = await dataclerk.filter(revision=revision)
        # if len(data["problems"]) == 0 and (revision["price_wire100_column"] > 0
        #                                    or revision["price_cash_column"] > 0):
        #     ready = data["ready"]
        #     await revision_client.is_manual(key=revision_key, manual=False)
        #     await price_client.add(supplier_id=supplier_id, prices=ready)
        #     await revision_client.publish_pricelist(key=key)
        # else:
        await revision_client.is_manual(key=revision_key, manual=True)
        # otherwise create task for manual upload

        info = {}

        from profiles.AgentExecutorClient import AgentExecutorClient
        agent_client = AgentExecutorClient()
        agent = await agent_client.get_one(agent_id=supplier_id)

        info["invalid_expiry"] = revision["ignore_expiry_count"]
        info["ignore_load"] = revision["ignore_load_count"]
        # todo: put correct seller name
        task = {"supplier_id": supplier_id,
                "url": url,
                "key": key,
                "filename": filename,
                "token": key_data["key"],
                "seller_name": agent["company_name"]}

        db = DataClerkTaskDB()
        result = await db.add(task)
        instance_id = result[self.uid]
        task[self.uid] = instance_id
        task["info"] = info
        await self.save({key_data["key"]: task})
        return {self.uid: instance_id}

    async def list(self):
        return await self._list()

    async def delete(self, task_id=None):
        task = await self.get([str(task_id)])
        db = DataClerkTaskDB()
        await db.remove(data=task[self.uid])
        await self.save({str(task_id): None})

    async def get_one(self, key=None):
        from modules.kinetic_core.Connector import db
        return await db.query("select *, current_timestamp from dataclerk_tasks where token = $1", (key,))

    async def complete(self, task_id=None):
        task = await self.get([str(task_id)])
        db = DataClerkTaskDB()
        await db.persist(data={
            "completed": 1
        }, filter=task[self.uid])
        await self.save({str(task_id): None})
        clerk_client = DataClerkClient()
        await clerk_client.remove(key=task["key"])

    async def size(self):
        return await self._size()
