#region import
import tornado.web
from web.handlers.BaseHandler import *
from pricelists.PriceListClient import PriceListClient
from pricelists.PriceListRevisionClient import PriceListRevisionClient
from dataclerk.task.DataClerkTaskClient import DataClerkTaskClient
#endregion

class PriceViewHandler(BaseHandler):

    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self, price_list_id):
        price_list_id = int(price_list_id)
        price_client = PriceListClient()
        price = await price_client.get_details(price_list_id=price_list_id)
        
        self.render("prices/view.html", price=price)
