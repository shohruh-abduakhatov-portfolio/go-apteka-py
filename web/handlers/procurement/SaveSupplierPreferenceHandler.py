from modules.pharmex.agent_users.AgentUserExecutorClient_ph import AgentUserExecutorClient_ph
from web.handlers.BaseHandler import *
import json
from modules.pharmex.utils.exception_handler import *


class SaveSupplierPreferenceHandler(BaseHandler):

    @throws_handler()
    @allowedRole(Role.PHARMA_CLIENT)
    async def post(self):
        params = json.loads(self.get_argument('values'))
        supplier_ids = params.get('supplier_ids', None)
        user = self.get_current_user()
        user_id = user["user_id"]
        new_suppliers = params.get('new_suppliers', None)

        user_client = AgentUserExecutorClient_ph()

        new_suppliers = {str(i): int(c) for i, c in new_suppliers.items()}

        user_details = await user_client.get_one(data={"user_id": user_id})
        inclusive_suppliers = user_details["inclusive_suppliers"] if "inclusive_suppliers" in user_details else {}

        #inclusive_suppliers.update(new_suppliers)

        #for new_id, new_cost in new_suppliers.items():
        #    if new_id not in inclusive_suppliers:
        #        del inclusive_suppliers[new_id]
        #

        agent_user_executor = AgentUserExecutorClient_ph()
        await agent_user_executor.modify(data={"inclusive_suppliers": new_suppliers, "user_id": user_id})

        self.write({"status": "success"})
        self.finish()
