import tornado.web
import json
from modules.kinetic_core.DateTimeEncoder import DateTimeEncoderCompact
from modules.pharmex.agent_users.AgentUserExecutorClient_ph import AgentUserExecutorClient_ph
from modules.pharmex.basket.BasketExecutorClient_ph import BasketExecutorClient_ph
from modules.pharmex.provision.ProvisionExecutorClient_ph import ProvisionExecutorClient_ph
from modules.business.warehouse.ProductsExecutorClient import ProductsExecutorClient
from web.handlers.BaseHandler import *
from modules.pharmex.utils.exception_handler import *


class CartContentsLoaderJSONHandler(BaseHandler):

    @throws_handler()
    @allowedRole(Role.PHARMA_CLIENT)
    async def post(self):
        
        basket_executor_client = BasketExecutorClient_ph()
        agent_user_ex = AgentUserExecutorClient_ph()
        provision_ex = ProvisionExecutorClient_ph()
        product_ex = ProductsExecutorClient()

        current_user = self.get_current_user()
        user_id = current_user["user_id"]

        agent_user = await agent_user_ex.get_one(data={"user_id": user_id})
        basket = await basket_executor_client.get_by_user_id(data={"user_id": user_id})

        data = {}
        result = []

        for prov_id, i in basket["provision_ids"].items():

            entry = {}

            provision = await provision_ex.get_one(data={"provision_id": prov_id})
            product = await product_ex.get_one(product_id=provision["product_id"])

            entry["provision_id"] = prov_id
            entry["product_id"] = provision["product_id"]
            entry["name"] = product["name"]
            entry["quantity"] = provision["quantity"]
            entry["manufacturer"] = product["manufacturer"]

            result.append(entry)

        data["result"] = result
        
        self.write(json.dumps(data, cls=DateTimeEncoderCompact))
