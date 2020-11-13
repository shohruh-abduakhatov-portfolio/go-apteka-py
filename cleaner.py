#!/usr/bin/python3.6
import os
os.environ['VITA_CONFIG'] = '/var/www/config.py'
import asyncio
import traceback
from datetime import datetime
import sys
import os
from elasticsearch_async import AsyncElasticsearch
sys.path.append(os.path.abspath(__file__ + "/../"))
sys.path.append(os.path.abspath(__file__ + "/../") + "/modules/business/")
print(os.path.abspath(__file__ + "/../") + "/modules/business/")

from modules.kinetic_core.Connector import db
from dataclerk.DataClerkClient import DataClerkClient


async def main(loop):
    list_keys = await db.list("select key from pharmex_pricelist_revision")
    clerk_client = DataClerkClient()

    for key in list_keys:
        print(key)
        await clerk_client.remove(key=key["key"])

loop = asyncio.get_event_loop()

result = loop.run_until_complete(main(loop))
