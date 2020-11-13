#region import
import simplejson as json
import logging
import traceback
from web.handlers.BaseHandler import *
import tornado.web
from modules.business.warehouse.ProductsExecutorClient import ProductsExecutorClient
#endregion

class SuggestProductNameHandler(BaseHandler):

    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self, name):
        client = ProductsExecutorClient()
        manufacturer_id = int(self.get_argument("manufacturer_id", default=0))
        try:
            result = await client.best_matches(name=name, manufacturer_id=manufacturer_id)
            self.write(json.dumps(
                result, 
                ignore_nan=True,
                ensure_ascii=False, 
                separators=(',', ':')))
            self.finish()
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            self.set_status(500)
            self.write({"error": "server error"})
            self.finish()
