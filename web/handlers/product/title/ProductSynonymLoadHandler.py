# region import
import tornado.web
import asyncio
import json
from operations.TitleExecutorClient import TitleExecutorClient
from modules.kinetic_core.DateTimeEncoder import DateTimeEncoderCompact
from warehouse.ProductsExecutorClient import ProductsExecutorClient
from operations.ManufacturerSynonymsExecutorClient import ManufacturerSynonymsExecutorClient
from web.handlers.BaseHandler import *
# endregion


class ProductSynonymLoadHandler(BaseHandler):

    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self, product_id):
        title_client = TitleExecutorClient()
        product_client = ProductsExecutorClient()
        product = await product_client.get_one(product_id=product_id)
        data = await title_client.get_one(data={"product_id": product_id})

        if data is not None and data != None:
            synonym_client = ManufacturerSynonymsExecutorClient()
            synonym = await synonym_client.get_one(data={"manufacturer_id": data["manufacturer"]})
            data["manufacturer_s"] = synonym["synonyms"]

        self.write(json.dumps({
            "data": data,
            'product': {"name": product["name"],
                        "manufacturer_id": product["manufacturer_id"],
                        "manufacturer": product["manufacturer"]}
        }, cls=DateTimeEncoderCompact))
        self.finish()
