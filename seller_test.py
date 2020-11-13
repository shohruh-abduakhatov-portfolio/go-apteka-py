#!/usr/bin/python3.6
import os
os.environ['VITA_CONFIG'] = '/var/www/config.py'
import asyncio
import traceback
from datetime import datetime
import sys, os
from elasticsearch_async import AsyncElasticsearch
sys.path.append(os.path.abspath(__file__ + "/../"))
sys.path.append(os.path.abspath(__file__ + "/../") + "/modules/vita/")
print(os.path.abspath(__file__ + "/../") + "/modules/vita/")
from dataclerk.DataClerkClient import DataClerkClient
from modules.business.warehouse.ProductsExecutorClient import ProductsExecutorClient
from manufacturer.ManufacturerClient import ManufacturerClient
from suppliers.SellerClient import SellerClient

async def main(loop):
    seller_client = SellerClient()
    result = await seller_client.add(agent_id=27, telegram_id=582364157)
    print(result)

loop = asyncio.get_event_loop()

result = loop.run_until_complete(main(loop))
