# region import
import tornado.web
import asyncio
from modules.business.warehouse.ProductsExecutorClient import ProductsExecutorClient
from web.handlers.BaseHandler import *
# endregion


class ProductListJSONHandler(BaseHandler):

    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self):
        q = self.get_argument("search[value]", default=None)
        offset = int(self.get_argument("start", default=0))
        limit = int(self.get_argument("limit", default=10))
        product_client = ProductsExecutorClient()
        if q is not None and len(q) > 2:

            autocomplete = await product_client.inner_search(q=q, offset=offset, limit=limit)
            data = []
            for item in autocomplete:
                data.append(item["_source"])
            result = {"count": 200, "data": data}
        # todo different sources for search and list
        else:
            result = await product_client.list(limit=limit, offset=offset)
        data = {
            "draw": self.get_argument("draw", default=1),
            "recordsTotal": result["count"],
            "recordsFiltered": result["count"],
        }
        l = list()
        for item in result["data"]:
            l.append([
                item["product_id"],
                item["name"],
                item["manufacturer"],
                item["product_id"],
                item["product_id"],
                item["product_id"]])
        data["data"] = l
        self.write(data)
        self.finish()
