from pricelists.PriceListClient import PriceListClient
import tornado.web

from modules.kinetic_core.DateTimeEncoder import DateTimeEncoderCompact
import asyncio
from web.handlers.BaseHandler import *
from modules.pharmex.basket.BasketExecutorClient_ph import BasketExecutorClient_ph
import json
import pandas as pd
import datetime
from modules.kinetic_core.Connector import db
import math

from web.handlers.procurement.procurement_helper import data


class ProcurementBasketMIVSResponseHandler_test(BaseHandler):

    @allowedRole(Role.PHARMA_CLIENT)
    async def post(self):
        basket_executor = BasketExecutorClient_ph()
        print('calling mivs')
        mivs_result = await basket_executor.calc_by_mivs_test(data=data)
        print('mivs request complete')
        self.write(mivs_result)
        self.finish()
