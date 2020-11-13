from modules.kinetic_core.AbstractExecutor import AbstractExecutor
from dataclerk.task.DataClerkTaskClient import DataClerkTaskClient


class PriceDownloadExecutor(AbstractExecutor):

    async def save(self, path, agent_id):
        result = await self._save_file(path=path)

        filename = path.split("/")[-1]
        data_clerk = DataClerkTaskClient()
        print("add pricelist to" + str(agent_id))
        await data_clerk.add(supplier_id=agent_id, key=result["key"], url=result["url"], filename=filename)
        return True
