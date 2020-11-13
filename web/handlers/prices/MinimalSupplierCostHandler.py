from modules.pharmex.agent_users.AgentUserExecutorClient_ph import AgentUserExecutorClient_ph
from web.handlers.BaseHandler import *
import json
from modules.pharmex.utils.exception_handler import *


class MinimalSupplierCostHandler(BaseHandler):

    @throws_handler()
    @allowedRole(Role.PHARMA_CLIENT)
    async def post(self):
        user = self.get_current_user()
        user_id = user["user_id"]

        supplier_id = int(self.get_argument("supplier_id", default=None))
        min_cost = int(self.get_argument("cost"))

        #agent_user_executor = AgentUserExecutorClient_ph()
        #await agent_user_executor.modify(data={"inclusive_suppliers": inclusive_suppliers, "user_id": user_id})

        self.write({"status": "success"})
        self.finish()
