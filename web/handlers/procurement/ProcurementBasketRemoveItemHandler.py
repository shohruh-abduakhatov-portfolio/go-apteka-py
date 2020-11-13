from pricelists.PriceListClient import PriceListClient
import tornado.web

from modules.kinetic_core.DateTimeEncoder import DateTimeEncoderCompact
import asyncio
from web.handlers.BaseHandler import *
from modules.pharmex.provision.ProvisionExecutorClient_ph import ProvisionExecutorClient_ph
from modules.pharmex.basket.BasketExecutorClient_ph import BasketExecutorClient_ph
import json
import traceback as tb
import datetime
from modules.kinetic_core.Connector import db
from modules.pharmex.utils.exception_handler import *


class ProcurementBasketRemoveItemHandler(BaseHandler):

    @throws_handler()
    @allowedRole(Role.PHARMA_CLIENT)
    async def post(self):

        provision_id = int(self.get_argument("provision_id", default=None))

        pharmex_provision_client = BasketExecutorClient_ph()
        basket_client = BasketExecutorClient_ph()

        current_user = self.get_current_user()
        user_id = current_user["user_id"]
        basket = await basket_client.get_by_user_id(data={"user_id": user_id})
        basket_id = int(basket["basket_id"])

        await basket_client.remove_provision(data={"provision_ids": [provision_id], "basket_id": basket_id})

        response = {"status": "success", "message": 'Удалено из корзины'}

        self.write(response)
        self.finish()
