#region import
import tornado.web
import asyncio
import json
from pricelists.PriceListClient import PriceListClient
from modules.kinetic_core.DateTimeEncoder import DateTimeEncoderCompact
from web.handlers.BaseHandler import *
#endregion

class PricesListJSONHandler(BaseHandler):

    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self):
        offset = int(self.get_argument("start", default=0))
        limit = int(self.get_argument("limit", default=10))
        pricelist_client = PriceListClient()
        result = await pricelist_client.paginate(limit=limit, offset=offset)
        data = {
            "draw": self.get_argument("draw", default=1),
            "recordsTotal": result["count"],
            "recordsFiltered": result["count"],
        }
        l = list()
        for item in result["data"]:
            l.append([
                item["price_list_id"],
                item["name"], 
                item["manufacturer"],
                item["supplier_id"], 
                item["quantity"],
                item["expiry"].strftime('%m.%Y'),
                item["wire25"],
                item["wire50"],
                item["wire75"],
                item["wire100"],
                item["cash"]
                ])
        data["data"] = l
        self.write(json.dumps(data, cls=DateTimeEncoderCompact))
        self.finish()
