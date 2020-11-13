from pricelists.PriceListClient import PriceListClient
import tornado.web

from modules.kinetic_core.DateTimeEncoder import DateTimeEncoderCompact
import asyncio
from web.handlers.BaseHandler import *
from pricelists.PriceListClient import PriceListClient
from modules.business.profiles.AgentExecutorClient import AgentExecutorClient
from modules.pharmex.basket.BasketExecutorClient_ph import BasketExecutorClient_ph
import json
import pandas as pd
import datetime
from modules.kinetic_core.Connector import db
from modules.business.profiles.auth.SMSVerificationClient import SMSVerificationClient
from modules.pharmex.agent_users.AgentUserExecutorClient_ph import AgentUserExecutorClient_ph


class SMSCodeRequestHandler(BaseHandler):

    async def post(self):

        from authorization.CpUserDB import CpUserDB

        phone = self.get_argument("phone", default=None)

        sms_client = SMSVerificationClient()
        agent_client = AgentUserExecutorClient_ph()
        db = CpUserDB()

        #exists = await db.get_by_phone_num(phone=phone)
        exists = await agent_client.get_by_phone(data={"phone": phone})

        if exists:
            response = await sms_client.generate(phone=phone, device_id='')
        else:
            response = False

        if response:
            self.write({"status": 'success'})

        else:
            self.write({"status": 'Пользователь с таким номером не найден'})

        self.finish()
