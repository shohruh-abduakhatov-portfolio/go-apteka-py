from modules.kinetic_core.AbstractExecutor import AbstractExecutor
from suppliers.SellerDB import SellerDB


class SellerExecutor(AbstractExecutor):

    params = {
        "agent_id": None,
        "telegram_id": None,
        "name": None,
    }

    def __init__(self, task):
        super().__init__(task)
        self.uid = "seller_id"

    async def add(self, agent_id=None, telegram_id=None, name=None):
        db = SellerDB()
        self.params["agent_id"] = agent_id
        self.params["telegram_id"] = telegram_id
        self.params["name"] = name
        result = await db.add(self.params)
        instance_id = result[self.uid]
        self.params[self.uid] = instance_id
        await self.save({"sid" + str(instance_id): self.params})
        await self.save({"tid" + str(telegram_id): instance_id})
        return {self.uid: instance_id}

    async def find_by_telegram_id(self, telegram_id):
        return await self.get(["tid"+str(telegram_id)])

    async def find_by_email(self, email):
        db = SellerDB()
        return await db.find_by_email(email)
