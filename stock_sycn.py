import asyncio
import sys
import os
os.environ['VITA_CONFIG'] = '/var/www/config.py'
# Add the ptdraft folder path to the sys.path list
sys.path.append('/Users/disturber/Documents/git/pharmex/')

sys.path.append(os.path.abspath(__file__ + "/../"))
print(os.path.abspath(__file__ + "/../"))
sys.path.append(os.path.abspath(__file__ + "/../modules/business/"))
import logging
import json
from datetime import time, datetime
from modules.kinetic_core import Logger
from elasticsearch_async import AsyncElasticsearch
from datetime import datetime
from warehouse.StockExecutorClient import StockExecutorClient
from modules.kinetic_core.DateTimeEncoder import DateTimeEncoderCompact

Logger.init(logging.DEBUG)
es = AsyncElasticsearch(hosts=['52.19.43.93'],
                        http_auth=('vita', 'g6t7y7h98hyg67'), port=8080)


async def add():
    await es.indices.delete(index="stockexecutor-index")
    stock_client = StockExecutorClient()
    stocks = await stock_client.list_all()
    info = await es.info()
    print(info)

    for stock in stocks:
        print(stock["stock_id"])
        res = await es.index(index="stockexecutor-index",
                             doc_type='item', id=stock["stock_id"], body=json.dumps(stock, cls=DateTimeEncoderCompact))

    es.indices.refresh(index="stockexecutor-index")


async def add_synonyms():
    await es.indices.delete(index="manufacturersynonymsexecutor-index")
    from operations.ManufacturerSynonymsExecutorClient import ManufacturerSynonymsExecutorClient
    synonym_client = ManufacturerSynonymsExecutorClient()
    stocks = await synonym_client.get_all()
    info = await es.info()
    print(info)

    for synonym_id, synonym in stocks.items():
        s = {
            "manufacturer_id": synonym["manufacturer_id"], "name": synonym["name"]}
        res = await es.index(index="manufacturersynonymsexecutor-index",
                             doc_type='item', id=synonym_id, body=json.dumps(s, cls=DateTimeEncoderCompact))

    es.indices.refresh(index="stockexecutor-index")


loop = asyncio.get_event_loop()
loop.run_until_complete(add())
loop.close()
