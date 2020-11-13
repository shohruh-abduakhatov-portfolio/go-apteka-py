import asyncio
import sys
import os
os.environ['VITA_CONFIG'] = '/var/www/config.py'
# Add the ptdraft folder path to the sys.path list
sys.path.append('/Users/disturber/Documents/git/pharmex/')

sys.path.append(os.path.abspath(__file__ + "/../"))
sys.path.append(os.path.abspath(__file__ + "/../modules/business/"))
import logging
from modules.kinetic_core import Logger
from elasticsearch_async import AsyncElasticsearch
from datetime import datetime
from supply.ProvisionExecutorClient import ProvisionExecutorClient
from warehouse.ProductsExecutorClient import ProductsExecutorClient
from suppliers.aliases.AgentFullAliasesClient import AgentFullAliasesClient
from warehouse.ProductsExecutor import ProductsExecutor
from transliterate import translit
Logger.init(logging.DEBUG)
es = AsyncElasticsearch(hosts=['52.19.43.93'],
                        http_auth=('vita', 'g6t7y7h98hyg67'), port=8080)


async def test():
    full_alias_client = AgentFullAliasesClient()
    match_name = await full_alias_client.find(alias_product="Эбуфен MR сусп 100мл",
                                              alias_manufacturer="МЕРРИМЕД ФАРМ-Узбекистан")
    print(match_name)


loop = asyncio.get_event_loop()
loop.create_task(test())
loop.run_forever()
