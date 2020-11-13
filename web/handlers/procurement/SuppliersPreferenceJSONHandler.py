from pricelists.PriceListClient import PriceListClient
import tornado.web

from modules.kinetic_core.DateTimeEncoder import DateTimeEncoderCompact
import asyncio
from web.handlers.BaseHandler import *
from modules.pharmex.utils.exception_handler import *
from pricelists.PriceListClient import PriceListClient
from modules.pharmex.agent_users.AgentUserExecutorClient_ph import AgentUserExecutorClient_ph
import json
import datetime
from modules.kinetic_core.Connector import db


class SuppliersPreferenceJSONHandler(BaseHandler):

    @throws_handler()
    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self):

        # TEST VALUE
        agent_id = self.get_argument('agent_id', default=None)
        print('agent id ', agent_id)

        all_suppliers = await db.list(
            "select agent_id, company_name, current_timestamp from pharmex_agents where not agent_id = $1 and pharmacy=0 "
            "order by company_name",
            (int(agent_id),))

        #print('all_suppliers ', all_suppliers)

        data = {
                "draw": self.get_argument("draw", default=1),
                "recordsTotal": len(all_suppliers),
                "recordsFiltered": len(all_suppliers),
            }

        l = list()

        agent_user_ex = AgentUserExecutorClient_ph()

        current_user = self.get_current_user()
        user_id = current_user["user_id"]

        agent_user = await agent_user_ex.get_one(data={"user_id": user_id})

        # await basket_executor_client.clear_basket(data={'basket_id': 15})

        excluded_titles = ["OOO", "ИП", "ООО", "ЧП"]

        for item in all_suppliers:
            sup_id = item["agent_id"]
            try:
                min_cost = agent_user["inclusive_suppliers"][str(sup_id)]
            except KeyError:
                min_cost = 300000

            company_name = item["company_name"]

            for x in excluded_titles:
                if x in item["company_name"][:3]:
                    company_name = company_name[len(x):]
                    break

            l.append([
                company_name,
                sup_id,
                min_cost
            ])

        data["result"] = l

        #print(data)

        self.write(json.dumps(data, cls=DateTimeEncoderCompact))
        self.finish()
