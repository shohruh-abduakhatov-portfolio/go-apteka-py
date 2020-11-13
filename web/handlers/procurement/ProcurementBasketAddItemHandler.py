from pricelists.PriceListClient import PriceListClient
import tornado.web

from modules.kinetic_core.DateTimeEncoder import DateTimeEncoderCompact
import asyncio
from web.handlers.BaseHandler import *
from modules.pharmex.utils.exception_handler import *

from modules.pharmex.provision.ProvisionExecutorClient_ph import ProvisionExecutorClient_ph
from modules.pharmex.basket.BasketExecutorClient_ph import BasketExecutorClient_ph

import json
import traceback as tb
import datetime


class ProcurementBasketAddItemHandler(BaseHandler):

    @throws_handler()
    @allowedRole(Role.PHARMA_CLIENT)
    async def post(self):

        product_id = int(self.get_argument("product_id", default=None))

        provision_type = str(self.get_argument("provision_type", default="standard"))
        quantity = self.get_argument("quantity", default=1)

        if isinstance(quantity, str) and quantity != '':
            quantity = int(quantity)

        if quantity == '':
            quantity = 1

        pharmex_provision_client = ProvisionExecutorClient_ph()
        basket_client = BasketExecutorClient_ph()

        # try:

        # except Exception as e:
        #    response = {"status": "error", "message": tb.format_exc(e)}


        current_user = self.get_current_user()
        user_id = current_user["user_id"]
        basket = await basket_client.get_by_user_id(data={"user_id": user_id})
        basket_id = basket["basket_id"]

        #provisions = [prov for prov in basket["provisions"]]
        #if len()
        product_ids = [provision["product_id"] for p_id, provision in basket["provisions"].items() if provision != None]

        if product_id not in product_ids:

            print('adding provision to basket')
            basket_prov_id = await basket_client.add_to_basket(data={"provision_type": provision_type, "product_id": product_id,
                                                    "quantity": quantity, "basket_id": basket_id})
            print('basket_prov_id: ', basket_prov_id)
            response = {"status": "success", "message": 'OK', "result": basket_prov_id, "quantity": quantity}
        else:
            print('product already exists in basket provisions')
            response = {"status": "success", "message": 'Продукт уже добавлен в корзину'}

        self.write(response)
        self.finish()

    get = post
